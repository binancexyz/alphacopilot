from __future__ import annotations

from src.formatters.heuristics import signal_quality_from_signal
from src.models.context import SignalContext
from src.models.schemas import AnalysisBrief, RiskTag

_GENERIC_SIGNAL_CONTEXTS = {
    "has a monitor-worthy setup, but the signal remains fragile.",
    "currently looks lower-conviction because the signal is weak or the risks remain elevated.",
}


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

    if score >= 5:
        return "High", "The signal has enough live context to support a more serious setup read."
    if score >= 3:
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
    elif ctx.signal_status in {"watch", "triggered", "bullish"}:
        base = "This matters because a visible setup can become actionable only if attention turns into durable confirmation instead of fading after the first reaction."
    else:
        base = "A signal only becomes decision-useful when it explains quality, follow-through, and invalidation — not just movement."

    extras: list[str] = []
    if ctx.smart_money_count > 0:
        extras.append(f"{ctx.smart_money_count} smart-money wallets are in the observed setup.")
    if ctx.signal_freshness != "UNKNOWN":
        extras.append(f"Timing reads as {ctx.signal_freshness.lower()} ({ctx.signal_age_hours:.1f}h old).")
    if ctx.exit_rate >= 70:
        extras.append(f"Exit rate is already high at {ctx.exit_rate:.0f}%, so the setup may be late.")
    elif ctx.exit_rate >= 40:
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

    if ctx.exit_rate >= 70:
        watch.append("whether smart-money exit pressure falls, because most tracked wallets may already be out")
    elif ctx.exit_rate >= 40:
        watch.append("whether exit pressure stays contained instead of drifting into a late setup")
    elif ctx.max_gain > 0:
        watch.append("whether prior upside follow-through can repeat without getting sold immediately")
    else:
        watch.append("whether the signal persists into the next cycle instead of fading quickly")

    if ctx.signal_freshness == "STALE":
        watch.append("whether fresh confirmation appears, because the original signal timing is already stale")
    elif ctx.signal_freshness == "AGING":
        watch.append("whether timing refreshes before the setup degrades further")
    return watch


def build_signal_brief(ctx: SignalContext) -> AnalysisBrief:
    quality = signal_quality_from_signal(ctx)
    conviction = "High" if quality == "High" and not ctx.major_risks else "Medium" if quality == "Medium" else "Low"
    evidence_level, evidence_note = _signal_evidence_level(ctx)

    risk_tags: list[RiskTag] = [RiskTag(name="Evidence Quality", level=evidence_level, note=evidence_note)]
    gate_level = "High" if ctx.audit_gate == "BLOCK" else "Medium" if ctx.audit_gate == "WARN" else "Low"
    if ctx.audit_flags or ctx.audit_gate != "ALLOW":
        note = ctx.blocked_reason or ", ".join(ctx.audit_flags) or "Audit returned caution flags."
        risk_tags.append(RiskTag(name="Audit Gate", level=gate_level, note=note))
    if ctx.signal_freshness != "UNKNOWN":
        risk_tags.append(RiskTag(name="Signal Timing", level="High" if ctx.signal_freshness == "STALE" else "Medium" if ctx.signal_freshness == "AGING" else "Low", note=f"{ctx.signal_freshness.title()} | {ctx.signal_age_hours:.1f}h old"))
    if ctx.exit_rate > 0:
        risk_tags.append(RiskTag(name="Exit Pressure", level="High" if ctx.exit_rate >= 70 else "Medium" if ctx.exit_rate >= 40 else "Low", note=f"Exit rate {ctx.exit_rate:.0f}%"))

    if ctx.audit_gate == "BLOCK":
        quick_verdict = f"{ctx.token} is blocked for bullish signal treatment because the audit layer is too dangerous to ignore."
        quality = "Blocked"
        conviction = "Low"
    elif evidence_level == "Low":
        quick_verdict = f"{ctx.token} is still a provisional signal read because the live setup evidence is too early or unmatched to trust aggressively."
        conviction = "Low"
    elif ctx.signal_status == "unmatched":
        quick_verdict = f"{ctx.token} does not currently have a matched live smart-money signal on the board, so this should be treated as a watchlist check rather than a true setup call."
    elif quality == "High":
        quick_verdict = f"{ctx.token} has a stronger signal than most watchlist noise, but it still needs follow-through to justify real conviction."
    elif quality == "Medium":
        quick_verdict = f"{ctx.token} has a usable signal setup, but it still looks fragile enough that weak confirmation could ruin it quickly."
    else:
        quick_verdict = f"{ctx.token} looks more like a headline signal than a strong setup right now; too much still depends on better confirmation or lower risk."

    top_risks = list(ctx.major_risks)
    if ctx.audit_gate == "BLOCK" and ctx.blocked_reason:
        top_risks.insert(0, ctx.blocked_reason)
    if not top_risks:
        if evidence_level == "Low":
            top_risks.append("Live signal confirmation is still too thin to treat this as a strong setup.")
        if ctx.exit_rate >= 70:
            top_risks.append(f"Late setup: {ctx.exit_rate:.0f}% of tracked smart money may already be out.")
        elif ctx.exit_rate >= 40:
            top_risks.append(f"Mixed setup: exit rate is already {ctx.exit_rate:.0f}%, so continuation quality is less clean.")
        if ctx.signal_freshness == "STALE":
            top_risks.append("Signal timing is stale and needs fresh confirmation.")
        elif ctx.signal_freshness == "AGING":
            top_risks.append("Signal timing is aging and can degrade quickly.")
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
