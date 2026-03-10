from __future__ import annotations

from src.formatters.heuristics import token_conviction, token_signal_quality
from src.models.context import TokenContext
from src.models.schemas import AnalysisBrief, RiskTag


def _token_price_line(ctx: TokenContext) -> str:
    if ctx.price > 0:
        return f"{ctx.display_name} is currently trading around ${ctx.price:,.2f}, so the setup is easier to frame than a token with missing price context."
    return f"{ctx.display_name} already has enough context to analyze, but price precision is still limited in this brief."


def _token_why_it_matters(ctx: TokenContext) -> str:
    pieces: list[str] = []
    if ctx.signal_trigger_context:
        pieces.append(ctx.signal_trigger_context)
    if ctx.market_rank_context and ctx.market_rank_context not in pieces:
        pieces.append(ctx.market_rank_context)
    if not pieces:
        pieces.append(_token_price_line(ctx))
    if ctx.liquidity > 0:
        pieces.append("Liquidity context is present, which makes this more useful than a purely narrative-only token mention.")
    return " ".join(pieces[:2]).strip()


def _token_watch_next(ctx: TokenContext) -> list[str]:
    watch: list[str] = []
    if ctx.signal_status in {"watch", "bullish", "triggered"}:
        watch.append("whether the current signal status improves from attention into real follow-through")
    else:
        watch.append("whether a clearer signal status appears instead of vague market attention")

    if ctx.liquidity > 0:
        watch.append("whether liquidity remains supportive as attention rotates")
    else:
        watch.append("whether reliable liquidity context becomes visible before conviction increases")

    if ctx.audit_flags:
        watch.append("whether contract and audit flags get cleaner or more concerning")
    else:
        watch.append("whether new structural risks appear as the setup develops")
    return watch


def build_token_brief(ctx: TokenContext) -> AnalysisBrief:
    quality = token_signal_quality(ctx)
    conviction = token_conviction(ctx)

    risk_tags: list[RiskTag] = []
    if ctx.audit_flags:
        risk_tags.append(RiskTag(name="Contract Risk", level="High", note=", ".join(ctx.audit_flags)))
    if ctx.liquidity <= 0:
        risk_tags.append(RiskTag(name="Liquidity Risk", level="Medium", note="Liquidity context is weak or missing."))
    else:
        risk_tags.append(RiskTag(name="Liquidity Risk", level="Low", note="Liquidity context is available, which improves research quality."))
    if ctx.market_rank_context:
        risk_tags.append(RiskTag(name="Narrative Risk", level="Medium", note=ctx.market_rank_context))

    if quality == "High" and conviction == "High":
        quick_verdict = f"{ctx.display_name} has a relatively clean token setup right now: signal quality is strong, basic liquidity context exists, and the risk stack is still manageable."
    elif quality == "High":
        quick_verdict = f"{ctx.display_name} has enough structure to take seriously, but conviction is still capped until the risk picture and follow-through get cleaner."
    elif quality == "Medium":
        quick_verdict = f"{ctx.display_name} is credible enough to keep on the screen, but it still looks like a conditional setup rather than a high-conviction one."
    else:
        quick_verdict = f"{ctx.display_name} currently looks thin on structure: too much still depends on missing context, weak signal quality, or elevated risk flags."

    top_risks = list(ctx.major_risks)
    if not top_risks:
        if ctx.audit_flags:
            top_risks.append("Contract-level flags still weigh on the setup.")
        if ctx.liquidity <= 0:
            top_risks.append("Liquidity context is missing or weak, which lowers confidence.")
        if not top_risks:
            top_risks.append("The setup still needs confirmation before attention turns into conviction.")

    return AnalysisBrief(
        entity=f"Token: {ctx.symbol}",
        quick_verdict=quick_verdict,
        signal_quality=quality,
        top_risks=top_risks,
        why_it_matters=_token_why_it_matters(ctx),
        what_to_watch_next=_token_watch_next(ctx),
        risk_tags=risk_tags,
        conviction=conviction,
        beginner_note="This is a research summary, not a buy/sell instruction.",
    )
