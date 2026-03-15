from __future__ import annotations

from src.analyzers.thresholds import (
    ATR_FALLBACK_PCT,
    ATR_ZONE_MULTIPLIER,
    EXIT_RATE_HIGH,
    EXIT_RATE_MODERATE,
    LIQUIDITY_DEEP,
    LIQUIDITY_MODERATE,
    LIQUIDITY_THIN,
    RR_GOOD,
    RR_MINIMUM_VIABLE,
)
from src.formatters.heuristics import signal_quality_from_signal
from src.models.context import SignalContext
from src.models.schemas import AnalysisBrief, RiskTag

_GENERIC_SIGNAL_CONTEXTS = {
    "has a monitor-worthy setup, but the signal remains fragile.",
    "currently looks lower-conviction because the signal is weak or the risks remain elevated.",
}


def _human_money(value: float) -> str:
    abs_value = abs(value)
    if abs_value >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:.1f}T"
    if abs_value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.1f}B"
    if abs_value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    if abs_value >= 1_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:,.2f}"


def _signal_invalidation(ctx: SignalContext) -> str:
    if ctx.audit_gate == "BLOCK":
        return "Breaks immediately if the audit state stays blocked."
    if ctx.trigger_price > 0 and ctx.current_price > 0:
        if ctx.current_price >= ctx.trigger_price:
            return "Breaks if price loses the trigger zone and follow-through fades."
        return "Still unproven until price reclaims the trigger zone with real follow-through."
    if ctx.exit_rate >= 70:
        return "Breaks if exit pressure stays elevated and fresh participation does not replace it."
    if ctx.signal_status == "unmatched":
        return "No smart-money follow-through."
    return "Breaks if confirmation does not improve in the next cycle."


def _signal_state_label(ctx: SignalContext, quality: str, evidence_level: str) -> str:
    if ctx.audit_gate == "BLOCK":
        return "blocked"
    if ctx.signal_status == "unmatched":
        return "unmatched"
    if ctx.signal_freshness == "STALE":
        return "stale"
    if evidence_level == "Low":
        return "thin"
    if ctx.exit_rate >= EXIT_RATE_HIGH:
        return "late"
    if ctx.trigger_price > 0 and ctx.current_price > 0:
        if ctx.current_price >= ctx.trigger_price and quality == "High":
            return "active"
        if ctx.current_price < ctx.trigger_price:
            return "early"
    if quality == "High":
        return "active"
    if quality == "Medium":
        return "early"
    return "fragile"


def _signal_evidence_level(ctx: SignalContext) -> tuple[str, str]:
    score = 0
    if ctx.signal_status != "unknown":
        score += 1
    if ctx.signal_status == "unmatched":
        score -= 1
    if ctx.trigger_price > 0:
        score += 1
    if ctx.current_price > 0:
        score += 1
    if ctx.supporting_context:
        score += 1
    if ctx.smart_money_count > 0:
        score += 1
    if ctx.signal_freshness != "UNKNOWN":
        score += 1
    if ctx.liquidity > 0:
        score += 1
    if ctx.volume_24h > 0:
        score += 1
    if ctx.funding_rate != 0 or ctx.long_short_ratio not in {0.0, 1.0}:
        score += 1

    if score >= 7:
        return "High", "The signal has enough live context to support a more serious setup read."
    if score >= 4:
        return "Medium", "The signal read is usable, but some live timing or confirmation context is still incomplete."
    return "Low", "The signal read is provisional because confirmation context is still early or unmatched."


def _signal_why_it_matters(ctx: SignalContext) -> str:
    if ctx.audit_gate == "BLOCK" and ctx.blocked_reason:
        return ctx.blocked_reason
    supporting = (ctx.supporting_context or "").strip()
    lower = supporting.lower()
    if supporting and not any(fragment in lower for fragment in _GENERIC_SIGNAL_CONTEXTS):
        base = supporting
    elif ctx.current_price > 0 and ctx.trigger_price > 0:
        base = f"The signal is more useful when you can compare current price (${ctx.current_price:,.2f}) against the trigger zone (${ctx.trigger_price:,.2f}) instead of reacting to noise alone."
    elif ctx.signal_status in {"watch", "triggered", "bullish", "active"}:
        base = "This matters because a visible setup can become actionable only if attention turns into durable confirmation instead of fading after the first reaction."
    else:
        base = "A signal only becomes decision-useful when it explains quality, follow-through, and invalidation — not just movement."

    extras: list[str] = []
    if ctx.smart_money_count > 0:
        extras.append(f"{ctx.smart_money_count} smart-money wallets are in the observed setup.")
    if ctx.signal_freshness != "UNKNOWN":
        extras.append(f"Timing reads as {ctx.signal_freshness.lower()} ({ctx.signal_age_hours:.1f}h old).")
    if ctx.liquidity > 0:
        extras.append(f"Visible liquidity is about ${ctx.liquidity:,.0f}.")
    if ctx.smart_money_inflow_usd > 0:
        extras.append(f"Smart-money inflow is visible at roughly ${ctx.smart_money_inflow_usd:,.0f}.")
    if ctx.funding_sentiment:
        futures_bits = [f"Futures positioning reads {ctx.funding_sentiment}"]
        if ctx.funding_rate != 0:
            futures_bits.append(f"funding {ctx.funding_rate * 100:+.4f}%")
        if ctx.long_short_ratio > 0:
            futures_bits.append(f"long/short {ctx.long_short_ratio:.2f}")
        extras.append(f"{futures_bits[0]}{' | ' + ' | '.join(futures_bits[1:]) if len(futures_bits) > 1 else ''}.")
    if ctx.exit_rate >= EXIT_RATE_HIGH:
        extras.append(f"Exit rate is already high at {ctx.exit_rate:.0f}%, so the setup may be late.")
    elif ctx.exit_rate >= EXIT_RATE_MODERATE:
        extras.append(f"Exit rate is mixed at {ctx.exit_rate:.0f}%, so continuation needs care.")
    return " ".join([base, *extras]).strip()


def _signal_watch_next(ctx: SignalContext) -> list[str]:
    watch: list[str] = []
    if ctx.audit_gate == "BLOCK":
        watch.append("do not act on the setup unless the audit state changes")
        return watch

    if ctx.trigger_price > 0 and ctx.current_price > 0:
        if ctx.current_price >= ctx.trigger_price:
            watch.append("whether price can hold above the current trigger zone instead of fading back through it")
        else:
            watch.append("whether price can reclaim the trigger zone with real confirmation")
    else:
        watch.append("whether the setup shows stronger price confirmation instead of only attention")

    if ctx.exit_rate >= EXIT_RATE_HIGH:
        watch.append("whether smart-money exit pressure falls, because most tracked wallets may already be out")
    elif ctx.exit_rate >= EXIT_RATE_MODERATE:
        watch.append("whether exit pressure stays contained instead of drifting into a late setup")
    elif ctx.max_gain > 0:
        watch.append("whether prior upside follow-through can repeat without getting sold immediately")
    else:
        watch.append("whether the signal persists into the next cycle instead of fading quickly")

    if ctx.signal_freshness == "STALE":
        watch.append("whether fresh confirmation appears, because the original signal timing is already stale")
    elif ctx.signal_freshness == "AGING":
        watch.append("whether timing refreshes before the setup degrades further")
    if abs(ctx.funding_rate) > 0.001:
        watch.append("whether extreme funding cools down before crowded positioning turns into a squeeze")
    elif ctx.long_short_ratio > 2.5:
        watch.append("whether crowded longs unwind instead of forcing a sharp flush")
    elif 0 < ctx.long_short_ratio < 0.5:
        watch.append("whether crowded shorts get squeezed or keep pressing the setup lower")
    return watch


def build_signal_brief(ctx: SignalContext) -> AnalysisBrief:
    quality = signal_quality_from_signal(ctx)
    conviction = "High" if quality == "High" and not ctx.major_risks else "Medium" if quality == "Medium" else "Low"
    evidence_level, evidence_note = _signal_evidence_level(ctx)
    state = _signal_state_label(ctx, quality, evidence_level)

    risk_tags: list[RiskTag] = [RiskTag(name="Evidence Quality", level=evidence_level, note=evidence_note)]
    gate_level = "High" if ctx.audit_gate == "BLOCK" else "Medium" if ctx.audit_gate == "WARN" else "Low"
    if ctx.audit_flags or ctx.audit_gate != "ALLOW":
        note = ctx.blocked_reason or ", ".join(ctx.audit_flags) or "Audit returned caution flags."
        risk_tags.append(RiskTag(name="Audit Gate", level=gate_level, note=note))
    if ctx.signal_freshness != "UNKNOWN":
        risk_tags.append(RiskTag(name="Signal Timing", level="High" if ctx.signal_freshness == "STALE" else "Medium" if ctx.signal_freshness == "AGING" else "Low", note=f"{ctx.signal_freshness.title()} | {ctx.signal_age_hours:.1f}h old"))
    if ctx.exit_rate > 0:
        risk_tags.append(RiskTag(name="Exit Pressure", level="High" if ctx.exit_rate >= 70 else "Medium" if ctx.exit_rate >= 40 else "Low", note=f"Exit rate {ctx.exit_rate:.0f}%"))
    if ctx.liquidity > 0:
        liquidity_level = "High" if ctx.liquidity >= LIQUIDITY_DEEP else "Medium" if ctx.liquidity >= LIQUIDITY_MODERATE else "Low"
        risk_tags.append(RiskTag(name="Liquidity", level=liquidity_level, note=f"Visible liquidity {ctx.liquidity:,.0f}"))
    if ctx.funding_sentiment or ctx.funding_rate != 0 or ctx.long_short_ratio not in {0.0, 1.0}:
        futures_level = "High" if abs(ctx.funding_rate) > 0.001 or ctx.long_short_ratio > 2.5 or (0 < ctx.long_short_ratio < 0.5) else "Medium"
        futures_note = []
        if ctx.funding_sentiment:
            futures_note.append(ctx.funding_sentiment.title())
        if ctx.funding_rate != 0:
            futures_note.append(f"funding {ctx.funding_rate * 100:+.4f}%")
        if ctx.long_short_ratio > 0:
            futures_note.append(f"L/S {ctx.long_short_ratio:.2f}")
        risk_tags.append(RiskTag(name="Futures Sentiment", level=futures_level, note=" | ".join(futures_note)))

    # Dynamic entry zone: ATR-based when high/low data is available, fallback to ±1%
    if ctx.trigger_price > 0:
        atr_pct = ATR_FALLBACK_PCT
        if ctx.price_high_24h > 0 and ctx.price_low_24h > 0 and ctx.price_high_24h > ctx.price_low_24h:
            atr_pct = (ctx.price_high_24h - ctx.price_low_24h) / ctx.trigger_price
            atr_pct = min(atr_pct * ATR_ZONE_MULTIPLIER, 0.10)  # cap at 10%
            atr_pct = max(atr_pct, 0.005)  # floor at 0.5%
        zone_low = ctx.trigger_price * (1.0 - atr_pct)
        zone_high = ctx.trigger_price * (1.0 + atr_pct)
        zone_note = f"${zone_low:,.2f} – ${zone_high:,.2f}"
        if atr_pct != ATR_FALLBACK_PCT:
            zone_note += f" (ATR-adjusted ±{atr_pct * 100:.1f}%)"
        risk_tags.append(RiskTag(name="Entry Zone", level="Info", note=zone_note))

        # Risk/Reward ratio: entry to recent high vs entry to invalidation
        if ctx.current_price > 0 and ctx.price_high_24h > 0:
            target = ctx.price_high_24h
            entry = ctx.trigger_price
            invalidation = zone_low
            reward = abs(target - entry) if target > entry else 0.0
            risk = abs(entry - invalidation) if entry > invalidation else abs(entry * atr_pct)
            if risk > 0:
                rr_ratio = reward / risk
                rr_level = "High" if rr_ratio >= RR_GOOD else "Medium" if rr_ratio >= RR_MINIMUM_VIABLE else "Low"
                rr_note = f"{rr_ratio:.1f}:1"
                if rr_ratio < RR_MINIMUM_VIABLE:
                    rr_note += " (below minimum viable)"
                risk_tags.append(RiskTag(name="Risk/Reward", level=rr_level, note=rr_note))

        # Take-profit suggestion from recent high/resistance
        if ctx.price_high_24h > 0 and ctx.price_high_24h > ctx.trigger_price:
            risk_tags.append(RiskTag(name="Take-Profit Zone", level="Info", note=f"~${ctx.price_high_24h:,.2f} (recent 24h high)"))

    risk_tags.append(RiskTag(name="Invalidation", level="Info", note=_signal_invalidation(ctx)))
    if ctx.max_gain > 0:
        risk_tags.append(RiskTag(name="Max Gain", level="Info", note=f"+{ctx.max_gain:.1f}%"))
    if ctx.smart_money_inflow_usd > 0:
        inflow_level = "High" if ctx.smart_money_inflow_usd >= 100_000 else "Medium"
        risk_tags.append(RiskTag(name="Smart Money Inflow", level=inflow_level, note=f"~{_human_money(ctx.smart_money_inflow_usd)}"))
    if ctx.volume_24h > 0:
        risk_tags.append(RiskTag(name="Volume 24h", level="Info", note=_human_money(ctx.volume_24h)))
    if ctx.volume_trend:
        vol_level = "High" if ctx.volume_trend == "spike" else "Medium" if ctx.volume_trend == "increasing" else "Low"
        risk_tags.append(RiskTag(name="Volume Trend", level=vol_level, note=ctx.volume_trend.title()))
    if ctx.market_cap > 0:
        risk_tags.append(RiskTag(name="Market Cap", level="Info", note=_human_money(ctx.market_cap)))

    # BTC correlation check
    if ctx.btc_change_24h != 0 and ctx.pct_change_24h != 0:
        relative = ctx.pct_change_24h - ctx.btc_change_24h
        if abs(ctx.btc_change_24h) >= 2 and relative < -2:
            risk_tags.append(RiskTag(name="BTC Drag", level="High", note=f"BTC {ctx.btc_change_24h:+.1f}% is dragging — token underperforming by {abs(relative):.1f}pp"))
        elif abs(ctx.btc_change_24h) >= 2 and relative > 2:
            risk_tags.append(RiskTag(name="Relative Strength", level="Medium", note=f"Outperforming BTC by {relative:.1f}pp despite BTC at {ctx.btc_change_24h:+.1f}%"))

    if state == "blocked":
        quick_verdict = "Blocked. Audit risk too high."
        quality = "Blocked"
        conviction = "Low"
    elif state == "unmatched":
        available: list[str] = []
        if ctx.current_price > 0:
            available.append("price")
        if ctx.funding_rate != 0 or ctx.long_short_ratio not in {0.0, 1.0}:
            available.append("futures")
        if ctx.audit_gate and ctx.audit_gate != "ALLOW":
            available.append("audit")
        if available:
            quick_verdict = f"No signal match. {', '.join(available).title()} context still visible."
        else:
            quick_verdict = "Watchlist only. No signal match."
        conviction = "Low"
    elif state == "thin":
        quick_verdict = "Thin setup. Needs live confirmation."
        conviction = "Low"
    elif state == "stale":
        quick_verdict = "Stale setup. Fresh trigger needed."
        conviction = "Low"
    elif state == "late":
        quick_verdict = "Active but late. Exit pressure is high."
        conviction = "Low"
    elif state == "active":
        quick_verdict = "Active setup. Trigger is holding."
        conviction = "Medium" if ctx.exit_rate >= 40 or ctx.audit_gate == "WARN" else "High"
    elif state == "early":
        quick_verdict = "Early setup. Trigger still needs reclaim."
        conviction = "Medium" if evidence_level == "High" else "Low"
    else:
        quick_verdict = "Fragile setup. Better confirmation needed."

    top_risks = list(ctx.major_risks)
    if ctx.audit_gate == "BLOCK" and ctx.blocked_reason:
        top_risks.insert(0, ctx.blocked_reason)
    if not top_risks:
        if state == "thin":
            top_risks.append("Live signal confirmation is still too thin to treat this as a strong setup.")
        if state == "unmatched":
            top_risks.append("No matched smart-money signal is visible on the current board.")
        if ctx.exit_rate >= EXIT_RATE_HIGH:
            top_risks.append(f"Late setup: {ctx.exit_rate:.0f}% of tracked smart money may already be out.")
        elif ctx.exit_rate >= EXIT_RATE_MODERATE:
            top_risks.append(f"Mixed setup: exit rate is already {ctx.exit_rate:.0f}%, so continuation quality is less clean.")
        if ctx.signal_freshness == "STALE":
            top_risks.append("Signal timing is stale and needs fresh confirmation.")
        elif ctx.signal_freshness == "AGING":
            top_risks.append("Signal timing is aging and can degrade quickly.")
        if 0 < ctx.liquidity < LIQUIDITY_THIN:
            top_risks.append("Visible liquidity is still thin, so execution quality may lag the signal headline.")
        if abs(ctx.funding_rate) > 0.001:
            top_risks.append("Futures funding is extreme, which raises squeeze and liquidation risk around the setup.")
        elif ctx.long_short_ratio > 2.5:
            top_risks.append("Long positioning looks crowded, so upside can still fail into a flush.")
        elif 0 < ctx.long_short_ratio < 0.5:
            top_risks.append("Short positioning looks crowded, so timing can get whippy even if the broader setup survives.")
        if ctx.trigger_price > 0 and ctx.current_price > 0 and ctx.current_price < ctx.trigger_price:
            top_risks.append("Price is still below the trigger zone, so confirmation remains incomplete.")
        if not top_risks:
            top_risks.append("Visible signals can fail quickly when follow-through does not arrive.")
        if ctx.audit_flags:
            top_risks.append("Contract or audit flags add structural downside to the setup.")

    return AnalysisBrief(
        entity=f"Signal: {ctx.token}",
        quick_verdict=quick_verdict,
        signal_quality=quality,
        top_risks=top_risks,
        why_it_matters=_signal_why_it_matters(ctx),
        what_to_watch_next=_signal_watch_next(ctx),
        risk_tags=risk_tags,
        conviction=conviction,
        beginner_note="A signal is not a guarantee. Treat it as a setup to validate, not a result to trust blindly.",
        audit_gate=ctx.audit_gate,
        blocked_reason=ctx.blocked_reason,
    )
