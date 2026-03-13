from __future__ import annotations

from src.formatters.heuristics import watch_today_signal_quality
from src.models.context import WatchTodayContext
from src.models.schemas import AnalysisBrief, BriefSection, RiskTag


LANE_LABELS = {
    "trending_now": "Trending Now",
    "smart_money_flow": "Smart Money Flow",
    "social_hype": "Social Hype",
    "meme_watch": "Meme Watch",
    "top_narratives": "Narrative",
    "top_picks": "Top Picks",
    "strongest_signals": "Signal Core",
    "exchange_board": "Exchange Board",
}


def _watch_lane_summary(ctx: WatchTodayContext) -> tuple[list[str], list[str]]:
    lanes = {
        "trending_now": bool(ctx.trending_now),
        "smart_money_flow": bool(ctx.smart_money_flow),
        "social_hype": bool(ctx.social_hype),
        "meme_watch": bool(ctx.meme_watch),
        "top_narratives": bool(ctx.top_narratives),
        "top_picks": bool(ctx.top_picks),
        "strongest_signals": bool(ctx.strongest_signals),
        "exchange_board": bool(ctx.exchange_board),
    }
    populated = [LANE_LABELS[key] for key, present in lanes.items() if present]
    sparse = [LANE_LABELS[key] for key, present in lanes.items() if not present]
    return populated, sparse


def _watch_evidence_level(ctx: WatchTodayContext) -> tuple[str, str]:
    populated, sparse = _watch_lane_summary(ctx)
    score = len(populated)

    if score >= 5:
        return "High", f"The daily board has strong lane coverage ({', '.join(populated[:4])})."
    if score >= 3:
        sparse_note = f" Sparse lanes: {', '.join(sparse[:3])}." if sparse else ""
        return "Medium", f"The daily board is usable, but some lanes are still sparse or uneven.{sparse_note}"
    sparse_note = f" Sparse lanes: {', '.join(sparse[:4])}." if sparse else ""
    return "Low", f"The daily board is provisional because too many market lanes are still sparse or missing.{sparse_note}"


def _watch_why_it_matters(ctx: WatchTodayContext) -> str:
    strongest = ", ".join(ctx.strongest_signals[:2]) if ctx.strongest_signals else "no clean signal leaders yet"
    narratives = ", ".join(ctx.top_narratives[:2]) if ctx.top_narratives else "no durable narrative leaders yet"
    exchange = ", ".join(ctx.exchange_board[:2]) if ctx.exchange_board else "no exchange board anchors yet"
    populated, sparse = _watch_lane_summary(ctx)
    lane_note = ""
    if sparse and populated:
        lane_note = f" Populated lanes: {', '.join(populated[:3])}. Sparse lanes: {', '.join(sparse[:2])}."
    elif sparse and not populated:
        lane_note = f" Most lanes are still sparse: {', '.join(sparse[:3])}."
    return f"Top signal lanes: {strongest}. Narrative heat: {narratives}. Exchange board: {exchange}. The edge today is ranking clean setups ahead of crowded or concentrated names.{lane_note}"



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
    if ctx.exchange_board:
        sections.append(BriefSection(title="🏦 Exchange Board", content="\n".join(f"- {item}" for item in ctx.exchange_board[:3])))
    if len(ctx.social_hype) >= 2 or (ctx.social_hype and not ctx.trending_now):
        sections.append(BriefSection(title="📣 Social Hype", content="\n".join(f"- {item}" for item in ctx.social_hype[:2])))
    if len(ctx.meme_watch) >= 2 or (ctx.meme_watch and not ctx.top_narratives):
        sections.append(BriefSection(title="🚀 Meme Watch", content="\n".join(f"- {item}" for item in ctx.meme_watch[:3])))
    if ctx.top_narratives:
        sections.append(BriefSection(title="🌊 Narrative", content="\n".join(f"- {item}" for item in ctx.top_narratives[:3])))
    if len(ctx.top_picks) >= 2 or (ctx.top_picks and (ctx.strongest_signals or ctx.exchange_board)):
        sections.append(BriefSection(title="👀 Today's Top 3", content="\n".join(f"- {item}" for item in ctx.top_picks[:3])))

    populated, sparse = _watch_lane_summary(ctx)
    if len(sparse) >= 2:
        sections.append(BriefSection(title="🧩 Lane Coverage", content=f"- Ready: {', '.join(populated[:4]) or 'none yet'}\n- Sparse: {', '.join(sparse[:4])}"))
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

    populated, sparse = _watch_lane_summary(ctx)

    signal_count = len(ctx.strongest_signals)
    attention_count = len(ctx.trending_now)
    smart_money_count = len(ctx.smart_money_flow)
    
    if signal_count >= 3 and smart_money_count >= 2:
        quick_verdict = "Heavy smart money accumulation. High conviction board."
    elif signal_count >= 3:
        quick_verdict = "Strong board. High selectivity needed."
    elif smart_money_count >= 3 and attention_count == 0:
        quick_verdict = "Smart money moving quietly. Watch closely."
    elif signal_count >= 1 and attention_count >= 1:
        quick_verdict = "Moderate board. Be selective." if len(sparse) < 2 else "Moderate board. selective rather than complete."
    elif signal_count >= 1 and attention_count == 0:
        quick_verdict = "Signal-led day. Low noise."
    elif attention_count >= 1 and signal_count == 0:
        quick_verdict = "Hype day. Caution."
    elif evidence_level == "Low":
        quick_verdict = "Quiet board. Hold posture."
        conviction = "Low"
    else:
        quick_verdict = "Quiet board. Hold posture."

    if evidence_level != "High" and len(sparse) >= 3:
        conviction = "Low"

    top_risks = list(ctx.major_risks)
    if not top_risks:
        if evidence_level == "Low":
            top_risks.append("Too many daily market lanes are still sparse, so this board should be treated as lower-confidence.")
        elif sparse:
            top_risks.append(f"Some board lanes are still sparse ({', '.join(sparse[:3])}), so coverage is selective rather than complete.")
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
