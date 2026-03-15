from __future__ import annotations

from src.analyzers.thresholds import (
    FUNDING_RATE_ELEVATED,
    FUNDING_RATE_EXTREME,
    OI_CHANGE_SIGNIFICANT,
)
from src.models.context import FuturesContext
from src.models.schemas import AnalysisBrief, BriefSection, RiskTag
from src.services.normalizers import normalize_futures_context
from src.utils.formatting import human_money as _human_money


def _funding_trend_note(ctx: FuturesContext) -> str:
    if ctx.funding_rate == 0:
        return ""
    parts: list[str] = []
    current = ctx.funding_rate * 100
    parts.append(f"now {current:+.4f}%")
    if ctx.funding_rate_8h_ago != 0:
        delta_8h = (ctx.funding_rate - ctx.funding_rate_8h_ago) * 100
        direction = "rising" if delta_8h > 0 else "falling"
        parts.append(f"8h ago {ctx.funding_rate_8h_ago * 100:+.4f}% ({direction})")
    if ctx.funding_rate_24h_ago != 0:
        delta_24h = (ctx.funding_rate - ctx.funding_rate_24h_ago) * 100
        direction = "rising" if delta_24h > 0 else "falling"
        parts.append(f"24h ago {ctx.funding_rate_24h_ago * 100:+.4f}% ({direction})")
    return " | ".join(parts)


def _oi_interpretation(ctx: FuturesContext) -> str:
    if ctx.oi_change_pct_24h == 0 and ctx.open_interest == 0:
        return ""
    parts: list[str] = []
    if ctx.open_interest > 0:
        parts.append(f"OI {ctx.open_interest:,.0f}")
    if ctx.oi_change_pct_24h != 0:
        direction = "rising" if ctx.oi_change_pct_24h > 0 else "falling"
        parts.append(f"24h {direction} {abs(ctx.oi_change_pct_24h):.1f}%")
        # OI + price correlation interpretation
        if ctx.price_change_pct_24h != 0:
            if ctx.oi_change_pct_24h > OI_CHANGE_SIGNIFICANT and ctx.price_change_pct_24h > 0:
                parts.append("conviction longs building")
            elif ctx.oi_change_pct_24h > OI_CHANGE_SIGNIFICANT and ctx.price_change_pct_24h < 0:
                parts.append("shorts accumulating — potential squeeze setup")
            elif ctx.oi_change_pct_24h < -OI_CHANGE_SIGNIFICANT and ctx.price_change_pct_24h < 0:
                parts.append("long liquidation cascade likely")
            elif ctx.oi_change_pct_24h < -OI_CHANGE_SIGNIFICANT and ctx.price_change_pct_24h > 0:
                parts.append("short squeeze unwinding")
    if ctx.oi_change_pct_4h != 0:
        parts.append(f"4h {ctx.oi_change_pct_4h:+.1f}%")
    return " | ".join(parts)


def _liquidation_note(ctx: FuturesContext) -> str:
    if ctx.liquidation_24h_long <= 0 and ctx.liquidation_24h_short <= 0:
        return ""
    parts: list[str] = []
    if ctx.liquidation_24h_long > 0:
        parts.append(f"longs liquidated {_human_money(ctx.liquidation_24h_long)}")
    if ctx.liquidation_24h_short > 0:
        parts.append(f"shorts liquidated {_human_money(ctx.liquidation_24h_short)}")
    total = ctx.liquidation_24h_long + ctx.liquidation_24h_short
    if total > 0:
        long_pct = (ctx.liquidation_24h_long / total * 100) if total > 0 else 0
        bias = "long-heavy" if long_pct >= 60 else "short-heavy" if long_pct <= 40 else "balanced"
        parts.append(f"bias: {bias}")
    return " | ".join(parts)


def analyze_futures(symbol: str, ctx: dict) -> AnalysisBrief:
    futures_ctx = normalize_futures_context(ctx)
    resolved = futures_ctx.symbol

    funding = futures_ctx.funding_rate
    oi = futures_ctx.open_interest
    ls = futures_ctx.long_short_ratio
    top_ls = futures_ctx.top_trader_long_short_ratio
    taker = futures_ctx.taker_buy_sell_ratio
    mark_price = futures_ctx.mark_price
    index_price = futures_ctx.index_price
    price_change = futures_ctx.price_change_pct_24h
    volume_24h = futures_ctx.ticker_volume_24h
    runtime_warning = futures_ctx.runtime_warning
    risks = list(futures_ctx.major_risks)

    sentiment = futures_ctx.funding_rate_sentiment
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

    # Enhance squeeze detection with OI + funding trends
    if abs(funding) > FUNDING_RATE_EXTREME and futures_ctx.oi_change_pct_24h > OI_CHANGE_SIGNIFICANT:
        squeeze = "high — extreme funding + rising OI"
    elif abs(funding) > FUNDING_RATE_ELEVATED and posture in ("crowded-long", "crowded-short"):
        squeeze = "high"

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
    if futures_ctx.oi_change_pct_24h != 0:
        why_bits.append(f"OI 24h {futures_ctx.oi_change_pct_24h:+.1f}%")
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
    # Add trend-based watch items
    if futures_ctx.oi_change_pct_24h > OI_CHANGE_SIGNIFICANT and price_change < 0:
        watch.insert(0, "rising OI + falling price suggests shorts are building — watch for squeeze reversal")
    if futures_ctx.liquidation_24h_long > 0 or futures_ctx.liquidation_24h_short > 0:
        watch.insert(0, "whether the liquidation cascade extends or stabilizes at current levels")

    tags = [
        RiskTag(name="Positioning", level="Medium", note=f"Futures sentiment reads {sentiment}."),
        RiskTag(name="Crowding", level="Info", note=crowding),
        RiskTag(name="Squeeze Risk", level="High" if "high" in squeeze.lower() else "Medium" if squeeze == "moderate" else "Info", note=squeeze),
    ]
    if runtime_warning:
        tags.append(RiskTag(name="Runtime", level="High", note=runtime_warning))

    # Funding trend tag
    funding_trend = _funding_trend_note(futures_ctx)
    if funding_trend:
        trend_level = "High" if abs(funding) > FUNDING_RATE_EXTREME else "Medium" if abs(funding) > FUNDING_RATE_ELEVATED else "Low"
        tags.append(RiskTag(name="Funding Trend", level=trend_level, note=funding_trend))

    # OI interpretation tag
    oi_note = _oi_interpretation(futures_ctx)
    if oi_note:
        oi_level = "High" if abs(futures_ctx.oi_change_pct_24h) > OI_CHANGE_SIGNIFICANT * 2 else "Medium" if abs(futures_ctx.oi_change_pct_24h) > OI_CHANGE_SIGNIFICANT else "Info"
        tags.append(RiskTag(name="Open Interest", level=oi_level, note=oi_note))

    # Liquidation tag
    liq_note = _liquidation_note(futures_ctx)
    if liq_note:
        total_liq = futures_ctx.liquidation_24h_long + futures_ctx.liquidation_24h_short
        liq_level = "High" if total_liq > 10_000_000 else "Medium" if total_liq > 1_000_000 else "Info"
        tags.append(RiskTag(name="Liquidations 24h", level=liq_level, note=liq_note))

    # Premium tag
    if mark_price > 0 and index_price > 0:
        premium_pct = ((mark_price - index_price) / index_price * 100)
        premium_level = "High" if abs(premium_pct) > 0.1 else "Medium" if abs(premium_pct) > 0.05 else "Low"
        tags.append(RiskTag(name="Basis/Premium", level=premium_level, note=f"{premium_pct:+.3f}% (mark vs index)"))

    sections = []
    positioning_lines = []
    if mark_price > 0:
        positioning_lines.append(f"- Mark price: ${mark_price:,.2f}")
    if funding != 0:
        positioning_lines.append(f"- Funding rate: {funding * 100:+.4f}%")
    if oi > 0:
        positioning_lines.append(f"- Open interest: {oi:,.0f}")
    if futures_ctx.oi_change_pct_24h != 0:
        positioning_lines.append(f"- OI change 24h: {futures_ctx.oi_change_pct_24h:+.1f}%")
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

    # Trend section
    trend_lines = []
    if funding_trend:
        trend_lines.append(f"- Funding trend: {funding_trend}")
    if oi_note:
        trend_lines.append(f"- OI read: {oi_note}")
    if liq_note:
        trend_lines.append(f"- Liquidations: {liq_note}")
    if trend_lines:
        sections.append(BriefSection(title="📈 Trend Context", content="\n".join(trend_lines)))

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
