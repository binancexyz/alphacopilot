from __future__ import annotations

from src.formatters.heuristics import signal_quality_from_signal
from src.models.context import SignalContext
from src.models.schemas import AnalysisBrief, RiskTag


def build_signal_brief(ctx: SignalContext) -> AnalysisBrief:
    quality = signal_quality_from_signal(ctx)
    conviction = "High" if quality == "High" and not ctx.major_risks else "Medium" if quality == "Medium" else "Low"

    risk_tags: list[RiskTag] = []
    if ctx.audit_flags:
        risk_tags.append(RiskTag(name="Contract Risk", level="High", note=", ".join(ctx.audit_flags)))
    risk_tags.append(RiskTag(name="Signal Fragility", level="Medium" if quality != "High" else "Low", note="Signals fail quickly when follow-through is weak."))
    risk_tags.append(RiskTag(name="Narrative Risk", level="Medium", note=ctx.supporting_context or "Attention may not convert into durable continuation."))

    quick_verdict = f"{ctx.token} has a monitor-worthy setup, but the signal remains fragile."
    if quality == "High":
        quick_verdict = f"{ctx.token} shows relatively strong signal quality, though confirmation and risk still matter."
    elif quality == "Low":
        quick_verdict = f"{ctx.token} currently looks lower-conviction because the signal is weak or the risks remain elevated."

    why_it_matters = ctx.supporting_context or "Signal tools are most useful when they explain quality and invalidation conditions instead of just flagging movement."

    return AnalysisBrief(
        entity=f"Signal: {ctx.token}",
        quick_verdict=quick_verdict,
        signal_quality=quality,
        top_risks=ctx.major_risks or ["Signal context is incomplete; treat this as lower-confidence."],
        why_it_matters=why_it_matters,
        what_to_watch_next=[
            "volume confirmation",
            "whether the signal persists into the next cycle",
            "whether contract or structural risks worsen",
        ],
        risk_tags=risk_tags,
        conviction=conviction,
        beginner_note="A signal is not a guarantee. Treat it as worth monitoring, not automatically correct.",
    )
