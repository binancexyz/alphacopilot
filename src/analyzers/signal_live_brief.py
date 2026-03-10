from __future__ import annotations

from src.formatters.heuristics import signal_quality_from_signal
from src.models.context import SignalContext
from src.models.schemas import AnalysisBrief, RiskTag

_GENERIC_SIGNAL_CONTEXTS = {
    "has a monitor-worthy setup, but the signal remains fragile.",
    "currently looks lower-conviction because the signal is weak or the risks remain elevated.",
}


def _signal_why_it_matters(ctx: SignalContext) -> str:
    supporting = (ctx.supporting_context or "").strip()
    lower = supporting.lower()
    if supporting and not any(fragment in lower for fragment in _GENERIC_SIGNAL_CONTEXTS):
        return supporting
    if ctx.current_price > 0 and ctx.trigger_price > 0:
        return f"The signal is more useful when you can compare current price (${ctx.current_price:,.2f}) against the trigger zone (${ctx.trigger_price:,.2f}) instead of reacting to noise alone."
    if ctx.signal_status in {"watch", "triggered", "bullish"}:
        return "This matters because a visible setup can become actionable only if attention turns into durable confirmation instead of fading after the first reaction."
    return "A signal only becomes decision-useful when it explains quality, follow-through, and invalidation — not just movement."


def _signal_watch_next(ctx: SignalContext) -> list[str]:
    watch: list[str] = []
    if ctx.trigger_price > 0 and ctx.current_price > 0:
        if ctx.current_price >= ctx.trigger_price:
            watch.append("whether price can hold above the current trigger zone instead of fading back through it")
        else:
            watch.append("whether price can reclaim the trigger zone with real confirmation")
    else:
        watch.append("whether the setup shows stronger price confirmation instead of only attention")

    if ctx.max_gain > 0:
        watch.append("whether prior upside follow-through can repeat without getting sold immediately")
    else:
        watch.append("whether the signal persists into the next cycle instead of fading quickly")

    if ctx.audit_flags:
        watch.append("whether contract or structural risk flags stay contained")
    else:
        watch.append("whether new structural risks appear as attention increases")
    return watch


def build_signal_brief(ctx: SignalContext) -> AnalysisBrief:
    quality = signal_quality_from_signal(ctx)
    conviction = "High" if quality == "High" and not ctx.major_risks else "Medium" if quality == "Medium" else "Low"

    risk_tags: list[RiskTag] = []
    if ctx.audit_flags:
        risk_tags.append(RiskTag(name="Contract Risk", level="High", note=", ".join(ctx.audit_flags)))
    risk_tags.append(
        RiskTag(
            name="Signal Fragility",
            level="Medium" if quality != "High" else "Low",
            note="Signals fail quickly when follow-through is weak or attention rotates away.",
        )
    )
    risk_tags.append(
        RiskTag(
            name="Narrative Risk",
            level="Medium",
            note=ctx.supporting_context or "Attention may not convert into durable continuation.",
        )
    )

    if quality == "High":
        quick_verdict = f"{ctx.token} has a stronger signal than most watchlist noise, but it still needs follow-through to justify real conviction."
    elif quality == "Medium":
        quick_verdict = f"{ctx.token} has a usable signal setup, but it still looks fragile enough that weak confirmation could ruin it quickly."
    else:
        quick_verdict = f"{ctx.token} looks more like a headline signal than a strong setup right now; too much still depends on better confirmation or lower risk."

    top_risks = list(ctx.major_risks)
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
    )
