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
    runtime_warning = str(ctx.get("runtime_warning") or "").strip()
    risks = [str(x) for x in ctx.get("major_risks", []) if str(x).strip()]

    sentiment = str(ctx.get("funding_rate_sentiment") or "neutral")
    if runtime_warning:
        verdict = f"{resolved} futures context is degraded right now."
        conviction = "Low"
    elif sentiment == "bullish" and ls > 1.2:
        verdict = f"{resolved} futures positioning leans crowded-long."
        conviction = "Medium"
    elif sentiment == "bearish" and ls < 0.9:
        verdict = f"{resolved} futures positioning leans pressured / defensive."
        conviction = "Medium"
    else:
        verdict = f"{resolved} futures positioning looks mixed rather than one-sided."
        conviction = "Medium"

    why_bits = []
    if mark_price > 0:
        why_bits.append(f"mark price ${mark_price:,.2f}")
    if funding != 0:
        why_bits.append(f"funding {funding * 100:+.4f}%")
    if oi > 0:
        why_bits.append(f"open interest {oi:,.0f}")
    if ls > 0:
        why_bits.append(f"long/short {ls:.2f}")
    if top_ls > 0:
        why_bits.append(f"top trader ratio {top_ls:.2f}")
    if taker > 0:
        why_bits.append(f"taker buy/sell {taker:.2f}")
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
    tags = [RiskTag(name="Positioning", level="Medium", note=f"Futures sentiment reads {sentiment}.")]
    if runtime_warning:
        tags.append(RiskTag(name="Runtime", level="High", note=runtime_warning))

    sections = []
    lines = []
    if mark_price > 0:
        lines.append(f"- Mark price: ${mark_price:,.2f}")
    if funding != 0:
        lines.append(f"- Funding rate: {funding * 100:+.4f}%")
    if oi > 0:
        lines.append(f"- Open interest: {oi:,.0f}")
    if ls > 0:
        lines.append(f"- Long/short ratio: {ls:.2f}")
    if top_ls > 0:
        lines.append(f"- Top trader ratio: {top_ls:.2f}")
    if taker > 0:
        lines.append(f"- Taker buy/sell: {taker:.2f}")
    if lines:
        sections.append(BriefSection(title="📊 Futures Positioning", content="\n".join(lines)))

    return AnalysisBrief(
        entity=f"Futures · {resolved}",
        quick_verdict=verdict,
        signal_quality="Medium" if not runtime_warning and len(lines) >= 3 else "Low",
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
