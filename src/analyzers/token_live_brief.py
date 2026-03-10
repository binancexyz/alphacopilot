from __future__ import annotations

from src.formatters.heuristics import token_conviction, token_signal_quality
from src.models.context import TokenContext
from src.models.schemas import AnalysisBrief, RiskTag


def build_token_brief(ctx: TokenContext) -> AnalysisBrief:
    quality = token_signal_quality(ctx)
    conviction = token_conviction(ctx)

    risk_tags: list[RiskTag] = []
    if ctx.audit_flags:
        risk_tags.append(RiskTag(name="Contract Risk", level="High", note=", ".join(ctx.audit_flags)))
    if ctx.liquidity <= 0:
        risk_tags.append(RiskTag(name="Liquidity Risk", level="Medium", note="Liquidity context is weak or missing."))
    else:
        risk_tags.append(RiskTag(name="Liquidity Risk", level="Low", note="Basic liquidity context is available."))
    if ctx.market_rank_context:
        risk_tags.append(RiskTag(name="Narrative Risk", level="Medium", note=ctx.market_rank_context))

    quick_verdict = f"{ctx.display_name} looks worth monitoring, but conviction still depends on confirmation and risk balance."
    if quality == "High" and conviction == "High":
        quick_verdict = f"{ctx.display_name} shows stronger-than-average signal quality with relatively cleaner structural context."
    elif quality == "Low":
        quick_verdict = f"{ctx.display_name} currently looks lower-conviction because signal quality is weak or risk context remains heavy."

    why_it_matters = ctx.signal_trigger_context or ctx.market_rank_context or (
        f"{ctx.display_name} may have useful signal value, but users need context on both upside and fragility rather than raw hype."
    )

    what_to_watch_next = [
        "signal confirmation",
        "liquidity follow-through",
        "whether risk flags improve or worsen",
    ]

    return AnalysisBrief(
        entity=f"Token: {ctx.symbol}",
        quick_verdict=quick_verdict,
        signal_quality=quality,
        top_risks=ctx.major_risks or ["Signal context is incomplete; treat this as lower-confidence."],
        why_it_matters=why_it_matters,
        what_to_watch_next=what_to_watch_next,
        risk_tags=risk_tags,
        conviction=conviction,
        beginner_note="This is a research summary, not a buy/sell instruction.",
    )
