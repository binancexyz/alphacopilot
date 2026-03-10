from __future__ import annotations

from src.formatters.conviction import conviction_label
from src.models.schemas import AnalysisBrief, RiskTag
from src.services.factory import get_market_data_service


def analyze_signal(token: str) -> AnalysisBrief:
    service = get_market_data_service()
    context = service.get_signal_context(token)
    risk_tags = [
        RiskTag(name="Signal Fragility", level="Medium", note="Signals fail quickly when momentum is not confirmed."),
        RiskTag(name="Narrative Risk", level="Medium", note="Attention may not convert into durable follow-through."),
    ]
    brief = AnalysisBrief(
        entity=f"Signal: {token}",
        quick_verdict=context.get("quick_context", f"{token} may have a monitor-worthy setup, but the signal needs confirmation before conviction improves."),
        signal_quality=f"{context.get('signal_quality', 'Medium')} — a usable early signal, but still fragile.",
        top_risks=context.get("risks", []),
        why_it_matters="Signal tools are most useful when they explain signal quality and invalidation conditions instead of just flagging movement.",
        what_to_watch_next=[
            "volume confirmation",
            "supporting liquidity context",
            "whether attention persists into the next cycle",
        ],
        risk_tags=risk_tags,
    )
    brief.conviction = conviction_label(brief.signal_quality, len(brief.top_risks))
    return brief
