from __future__ import annotations

from src.formatters.conviction import conviction_label
from src.models.schemas import AnalysisBrief, RiskTag
from src.services.factory import get_market_data_service


def watch_today() -> AnalysisBrief:
    service = get_market_data_service()
    context = service.get_watch_today_context()
    risk_tags = [
        RiskTag(name="Narrative Risk", level="High", note="Fast rotation can make trend-following noisy."),
        RiskTag(name="Contract Risk", level="Medium", note="Some trending assets may still carry non-trivial contract concerns."),
    ]
    brief = AnalysisBrief(
        entity="Market Watch",
        quick_verdict=context.get("quick_context", "Today’s market looks active, but filtering matters more than chasing broad noise."),
        signal_quality=f"{context.get('signal_quality', 'Medium')} — there is opportunity, but selectivity is more important than speed.",
        top_risks=context.get("risks", []),
        why_it_matters="When multiple narratives heat up at once, users need prioritization and risk filtering more than more dashboards.",
        what_to_watch_next=[
            "top narratives with real liquidity support",
            "signals that persist beyond the first attention spike",
            "risk mismatches between hype and contract quality",
        ],
        risk_tags=risk_tags,
    )
    brief.conviction = conviction_label(brief.signal_quality, len(brief.top_risks))
    return brief
