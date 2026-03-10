from __future__ import annotations

from src.formatters.heuristics import watch_today_signal_quality
from src.models.context import WatchTodayContext
from src.models.schemas import AnalysisBrief, RiskTag


def build_watchtoday_brief(ctx: WatchTodayContext) -> AnalysisBrief:
    quality = watch_today_signal_quality(ctx)
    conviction = "Medium" if quality in {"High", "Medium"} else "Low"

    risk_tags: list[RiskTag] = []
    if ctx.risk_zones:
        risk_tags.append(RiskTag(name="Narrative Risk", level="High", note=", ".join(ctx.risk_zones[:3])))
    if ctx.strongest_signals:
        risk_tags.append(RiskTag(name="Signal Density", level="Medium", note=f"{len(ctx.strongest_signals)} active signal areas identified."))

    quick_verdict = ctx.market_takeaway or "Today’s market looks active, but filtering matters more than chasing broad noise."
    why_it_matters = "When multiple narratives heat up at once, users need prioritization and risk filtering more than more dashboards."

    what_to_watch_next = [
        "top narratives with real liquidity support",
        "signals that persist beyond the first attention spike",
        "risk mismatches between hype and contract quality",
    ]

    top_risks = ctx.major_risks or ["Broader market context is incomplete; treat this daily brief as lower-confidence."]

    return AnalysisBrief(
        entity="Market Watch",
        quick_verdict=quick_verdict,
        signal_quality=quality,
        top_risks=top_risks,
        why_it_matters=why_it_matters,
        what_to_watch_next=what_to_watch_next,
        risk_tags=risk_tags,
        conviction=conviction,
        beginner_note="Not everything trending is worth chasing. Strong attention and strong quality are not the same thing.",
    )
