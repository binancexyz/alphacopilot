from __future__ import annotations

from src.models.schemas import AnalysisBrief, BriefSection, RiskTag


def analyze_futures(symbol: str, ctx: dict) -> AnalysisBrief:
    resolved = str(ctx.get("symbol") or symbol).upper()
    funding = float(ctx.get("funding_rate") or 0.0)
    oi = float(ctx.get("open_interest") or 0.0)
    ls = float(ctx.get("long_short_ratio") or 0.0)
    top_ls = float(ctx.get("top_trader_long_short_ratio") or 0.0)
    taker = float(ctx.get("taker_buy_sell_ratio") or 0.0)
    mark_price = float(ctx.get("mark_price") or 0.0)
    index_price = float(ctx.get("index_price") or 0.0)
    price_change = float(ctx.get("price_change_pct_24h") or 0.0)
    volume_24h = float(ctx.get("ticker_volume_24h") or 0.0)
    runtime_warning = str(ctx.get("runtime_warning") or "").strip()
    risks = [str(x) for x in ctx.get("major_risks", []) if str(x).strip()]

    sentiment = str(ctx.get("funding_rate_sentiment") or "neutral")
    crowding = "balanced"
    squeeze = "low"
    posture = "mixed"
    if ls >= 1.25 and top_ls >= 1.02:
        crowding = "crowded longs"
        squeeze = "long squeeze risk"
        posture = "crowded-long"
    elif 0 < ls <= 0.9 and 0 < top_ls <= 0.98:
        crowding = "crowded shorts"
        squeeze = "short squeeze risk"
        posture = "crowded-short"
    elif taker >= 1.03 and sentiment != "bearish":
        crowding = "buyers pressing"
        squeeze = "moderate"
        posture = "buyers in control"
    elif 0 < taker <= 0.97 and sentiment != "bullish":
        crowding = "sellers pressing"
        squeeze = "moderate"
        posture = "sellers in control"

    if runtime_warning:
        verdict = f"{resolved} futures context is degraded right now."
        conviction = "Low"
    elif posture == "crowded-long":
        verdict = f"{resolved} futures look crowded-long with squeeze risk if momentum slips."
        conviction = "Medium"
    elif posture == "crowded-short":
        verdict = f"{resolved} futures lean short-heavy, which keeps squeeze risk alive to the upside."
        conviction = "Medium"
    elif posture == "buyers in control":
        verdict = f"{resolved} futures show buyers pressing, but positioning is not fully stretched yet."
        conviction = "Medium"
    elif posture == "sellers in control":
        verdict = f"{resolved} futures show sellers pressing, but positioning is not fully one-sided yet."
        conviction = "Medium"
    else:
        verdict = f"{resolved} futures positioning looks mixed rather than one-sided."
        conviction = "Medium"

    why_bits = []
    if mark_price > 0:
        why_bits.append(f"mark ${mark_price:,.2f}")
    if index_price > 0:
        premium_pct = ((mark_price - index_price) / index_price * 100) if mark_price > 0 else 0.0
        why_bits.append(f"premium {premium_pct:+.3f}%")
    if funding != 0:
        why_bits.append(f"funding {funding * 100:+.4f}%")
    if oi > 0:
        why_bits.append(f"OI {oi:,.0f}")
    if ls > 0:
        why_bits.append(f"L/S {ls:.2f}")
    if top_ls > 0:
        why_bits.append(f"top trader {top_ls:.2f}")
    if taker > 0:
        why_bits.append(f"taker {taker:.2f}")
    if volume_24h > 0:
        why_bits.append(f"24h vol ${volume_24h:,.0f}")
    if price_change:
        why_bits.append(f"24h {price_change:+.2f}%")
    if runtime_warning:
        why_bits.append(runtime_warning)
    why = (
        f"This reads Binance Futures positioning for {resolved}. " + ", ".join(why_bits) + "."
        if why_bits
        else f"This reads Binance Futures positioning for {resolved}, but the current payload is thin."
    )

    watch = [
        "whether funding keeps stretching in one direction and increases squeeze risk",
        "whether open interest expands with price or diverges against it",
        "whether long/short and taker flow start confirming the same side instead of fighting each other",
    ]
    tags = [
        RiskTag(name="Positioning", level="Medium", note=f"Futures sentiment reads {sentiment}."),
        RiskTag(name="Crowding", level="Info", note=crowding),
        RiskTag(name="Squeeze Risk", level="Info", note=squeeze),
    ]
    if runtime_warning:
        tags.append(RiskTag(name="Runtime", level="High", note=runtime_warning))

    sections = []
    positioning_lines = []
    if mark_price > 0:
        positioning_lines.append(f"- Mark price: ${mark_price:,.2f}")
    if funding != 0:
        positioning_lines.append(f"- Funding rate: {funding * 100:+.4f}%")
    if oi > 0:
        positioning_lines.append(f"- Open interest: {oi:,.0f}")
    if volume_24h > 0:
        positioning_lines.append(f"- 24h volume: ${volume_24h:,.0f}")
    if positioning_lines:
        sections.append(BriefSection(title="📊 Futures Positioning", content="\n".join(positioning_lines)))

    evidence_lines = []
    if ls > 0:
        evidence_lines.append(f"- Long/short ratio: {ls:.2f}")
    if top_ls > 0:
        evidence_lines.append(f"- Top trader ratio: {top_ls:.2f}")
    if taker > 0:
        evidence_lines.append(f"- Taker buy/sell: {taker:.2f}")
    if index_price > 0 and mark_price > 0:
        premium_pct = ((mark_price - index_price) / index_price * 100)
        evidence_lines.append(f"- Mark/index premium: {premium_pct:+.3f}%")
    if evidence_lines:
        sections.append(BriefSection(title="🧭 Positioning Evidence", content="\n".join(evidence_lines)))

    return AnalysisBrief(
        entity=f"Futures · {resolved}",
        quick_verdict=verdict,
        signal_quality="Medium" if not runtime_warning and (len(positioning_lines) + len(evidence_lines)) >= 4 else "Low",
        top_risks=risks,
        why_it_matters=why,
        what_to_watch_next=watch,
        risk_tags=tags,
        sections=sections,
        conviction=conviction,
        beginner_note="Futures positioning can stay crowded longer than expected. Use it as posture context, not a stand-alone signal.",
        runtime_state=ctx.get("runtime_state"),
        runtime_warning=ctx.get("runtime_warning"),
    )
