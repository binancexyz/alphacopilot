from __future__ import annotations

from src.formatters.heuristics import watch_today_signal_quality
from src.models.context import WatchTodayContext
from src.models.schemas import AnalysisBrief, RiskTag


def _watch_why_it_matters(ctx: WatchTodayContext) -> str:
    narrative_count = len(ctx.top_narratives)
    signal_count = len(ctx.strongest_signals)
    if narrative_count or signal_count:
        return (
            f"The market is throwing up {narrative_count} narrative lane(s) and {signal_count} stronger signal area(s), "
            "so the job is no longer finding movement — it is filtering for durability and cleaner risk." 
        )
    return "When market context is noisy, prioritization matters more than simply tracking what is trending."


def _watch_next(ctx: WatchTodayContext) -> list[str]:
    watch: list[str] = []
    if ctx.top_narratives:
        watch.append(f"whether top narratives like {', '.join(ctx.top_narratives[:2])} keep attracting real follow-through")
    else:
        watch.append("whether any narrative starts showing durable strength instead of one-cycle attention")

    if ctx.strongest_signals:
        watch.append(f"whether stronger signals such as {', '.join(ctx.strongest_signals[:2])} persist beyond the first spike")
    else:
        watch.append("whether strong signal clusters emerge instead of scattered noise")

    if ctx.risk_zones:
        watch.append(f"whether risk pockets like {', '.join(ctx.risk_zones[:2])} cool off or keep widening")
    else:
        watch.append("whether hype starts outrunning contract quality and liquidity")
    return watch


def build_watchtoday_brief(ctx: WatchTodayContext) -> AnalysisBrief:
    quality = watch_today_signal_quality(ctx)
    conviction = "Medium" if quality in {"High", "Medium"} else "Low"

    risk_tags: list[RiskTag] = []
    if ctx.risk_zones:
        risk_tags.append(RiskTag(name="Narrative Risk", level="High", note=", ".join(ctx.risk_zones[:3])))
    if ctx.strongest_signals:
        risk_tags.append(RiskTag(name="Signal Density", level="Medium", note=f"{len(ctx.strongest_signals)} active signal areas identified."))

    if ctx.market_takeaway:
        quick_verdict = ctx.market_takeaway
    elif quality == "High":
        quick_verdict = "There is real opportunity on the board today, but the edge comes from filtering, not from chasing every active narrative."
    elif quality == "Medium":
        quick_verdict = "The tape is active enough to matter, but selectivity still matters more than raw participation."
    else:
        quick_verdict = "Today looks noisier than clean, so preservation and filtering matter more than excitement."

    top_risks = list(ctx.major_risks)
    if not top_risks:
        if ctx.risk_zones:
            top_risks.append(f"Risk is clustering around {', '.join(ctx.risk_zones[:2])}, which can distort attention.")
        else:
            top_risks.append("Broader market context is incomplete; treat this daily brief as lower-confidence.")
        if ctx.top_narratives and not ctx.strongest_signals:
            top_risks.append("Narratives are visible, but signal quality inside them is still uneven.")

    return AnalysisBrief(
        entity="Market Watch",
        quick_verdict=quick_verdict,
        signal_quality=quality,
        top_risks=top_risks,
        why_it_matters=_watch_why_it_matters(ctx),
        what_to_watch_next=_watch_next(ctx),
        risk_tags=risk_tags,
        conviction=conviction,
        beginner_note="Not everything trending deserves capital or attention. Strong activity and strong quality are not the same thing.",
    )
