from __future__ import annotations

from src.formatters.heuristics import watch_today_signal_quality
from src.models.context import WatchTodayContext
from src.models.schemas import AnalysisBrief, BriefSection, RiskTag


def _watch_evidence_level(ctx: WatchTodayContext) -> tuple[str, str]:
    score = 0
    if ctx.trending_now:
        score += 1
    if ctx.smart_money_flow:
        score += 1
    if ctx.social_hype:
        score += 1
    if ctx.meme_watch:
        score += 1
    if ctx.top_narratives:
        score += 1
    if ctx.top_picks:
        score += 1
    if ctx.strongest_signals:
        score += 1

    if score >= 5:
        return "High", "The daily board has enough populated lanes to support a more useful market read."
    if score >= 3:
        return "Medium", "The daily board is usable, but some lanes are still sparse or uneven."
    return "Low", "The daily board is provisional because too many market lanes are still sparse or missing."


def _watch_why_it_matters(ctx: WatchTodayContext) -> str:
    strongest = ", ".join(ctx.strongest_signals[:2]) if ctx.strongest_signals else "no clean signal leaders yet"
    narratives = ", ".join(ctx.top_narratives[:2]) if ctx.top_narratives else "no durable narrative leaders yet"
    return f"Top signal lanes: {strongest}. Narrative heat: {narratives}. The edge today is ranking clean setups ahead of crowded or concentrated names."



def _watch_next(ctx: WatchTodayContext) -> list[str]:
    watch: list[str] = []
    if ctx.top_picks:
        watch.append(f"whether the lead idea stays with {ctx.top_picks[0]} instead of fading into noise")
    elif ctx.strongest_signals:
        watch.append(f"whether the cleanest setup stays with {ctx.strongest_signals[0]} instead of rolling over fast")
    else:
        watch.append("whether a genuinely clean setup appears instead of scattered noise")

    if ctx.top_narratives:
        watch.append(f"whether attention in {', '.join(ctx.top_narratives[:2])} stays durable instead of turning into rotation-chasing")
    else:
        watch.append("whether any narrative starts separating from the pack with real follow-through")

    if ctx.risk_zones:
        watch.append(f"whether risk pockets like {', '.join(ctx.risk_zones[:2])} cool down or keep trapping late attention")
    else:
        watch.append("whether concentration, caution flags, or late flows start overpowering the cleaner setups")
    return watch



def _watch_sections(ctx: WatchTodayContext) -> list[BriefSection]:
    sections: list[BriefSection] = []
    if ctx.trending_now:
        sections.append(BriefSection(title="🔥 Trending Now", content="\n".join(f"- {item}" for item in ctx.trending_now[:3])))
    if ctx.smart_money_flow:
        sections.append(BriefSection(title="🧠 Smart Money Flow", content="\n".join(f"- {item}" for item in ctx.smart_money_flow[:3])))
    if ctx.social_hype:
        sections.append(BriefSection(title="📣 Social Hype", content="\n".join(f"- {item}" for item in ctx.social_hype[:2])))
    if ctx.meme_watch:
        sections.append(BriefSection(title="🚀 Meme Watch", content="\n".join(f"- {item}" for item in ctx.meme_watch[:3])))
    if ctx.top_narratives:
        sections.append(BriefSection(title="🌊 Narrative", content="\n".join(f"- {item}" for item in ctx.top_narratives[:3])))
    if ctx.top_picks:
        sections.append(BriefSection(title="👀 Today's Top 3", content="\n".join(f"- {item}" for item in ctx.top_picks[:3])))
    return sections



def build_watchtoday_brief(ctx: WatchTodayContext) -> AnalysisBrief:
    quality = watch_today_signal_quality(ctx)
    conviction = "Medium" if quality in {"High", "Medium"} else "Low"
    evidence_level, evidence_note = _watch_evidence_level(ctx)

    risk_tags: list[RiskTag] = [RiskTag(name="Evidence Quality", level=evidence_level, note=evidence_note)]
    if ctx.risk_zones:
        risk_tags.append(RiskTag(name="Narrative Risk", level="High", note=", ".join(ctx.risk_zones[:3])))
    if ctx.strongest_signals:
        risk_tags.append(RiskTag(name="Signal Density", level="Medium", note=f"{len(ctx.strongest_signals)} active signal areas identified."))
    if ctx.top_narratives:
        risk_tags.append(RiskTag(name="Hot Narratives", level="Medium", note=", ".join(ctx.top_narratives[:3])))

    if evidence_level == "Low":
        quick_verdict = "Today’s board is still provisional because too many market lanes are sparse, so filtering matters more than confidence."
        conviction = "Low"
    elif ctx.market_takeaway:
        quick_verdict = ctx.market_takeaway
    elif quality == "High":
        quick_verdict = "There is real opportunity on the board today, but the edge comes from ranking clean setups ahead of noisy narratives."
    elif quality == "Medium":
        quick_verdict = "There is enough movement to care today, but only a small part of it looks worth trusting."
    else:
        quick_verdict = "Today looks noisier than clean, so preservation and filtering matter more than excitement."

    top_risks = list(ctx.major_risks)
    if not top_risks:
        if evidence_level == "Low":
            top_risks.append("Too many daily market lanes are still sparse, so this board should be treated as lower-confidence.")
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
        sections=_watch_sections(ctx),
        conviction=conviction,
        beginner_note="Not everything trending deserves capital or attention. Strong activity and strong quality are not the same thing.",
    )
