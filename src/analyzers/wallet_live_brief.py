from __future__ import annotations

from src.formatters.heuristics import wallet_signal_quality
from src.models.context import WalletContext
from src.models.schemas import AnalysisBrief, RiskTag


def _format_holding_summary(ctx: WalletContext) -> str:
    if not ctx.top_holdings:
        return "Top holding detail is limited, so this wallet still needs more behavior context before strong conclusions."

    top_bits = [f"{holding.symbol} ({holding.weight_pct:.1f}%)" for holding in ctx.top_holdings[:2]]
    return f"Top visible holdings are {', '.join(top_bits)}, which gives a better clue about style and concentration than wallet size alone."


def _wallet_why_it_matters(ctx: WalletContext) -> str:
    pieces: list[str] = []
    if ctx.portfolio_value > 0:
        pieces.append(f"This wallet tracks roughly ${ctx.portfolio_value:,.0f} across {ctx.holdings_count} holding(s), so it is large enough to inspect for behavior rather than treating it as random dust.")
    elif ctx.holdings_count > 0:
        pieces.append(f"This wallet shows {ctx.holdings_count} holding(s), which is enough to inspect for concentration and rotation patterns.")

    pieces.append(_format_holding_summary(ctx))
    return " ".join(pieces[:2]).strip()


def _wallet_watch_next(ctx: WalletContext) -> list[str]:
    watch: list[str] = []
    if ctx.change_24h > 0:
        watch.append("whether recent gains are being held, expanded, or rotated out of")
    elif ctx.change_24h < 0:
        watch.append("whether recent drawdown leads to rotation, defense, or fresh accumulation")
    else:
        watch.append("whether the wallet starts rotating into new assets or stays static")

    if ctx.top_concentration_pct >= 70:
        watch.append("whether concentration keeps increasing or begins to spread across more holdings")
    else:
        watch.append("whether top holding concentration stays controlled as new positions appear")

    if ctx.notable_exposures:
        watch.append(f"whether exposure to {', '.join(ctx.notable_exposures[:2])} proves early, crowded, or late")
    else:
        watch.append("whether the wallet starts clustering around a clearer narrative")
    return watch


def build_wallet_brief(ctx: WalletContext) -> AnalysisBrief:
    quality = wallet_signal_quality(ctx)
    conviction = "Medium" if quality == "Medium" and len(ctx.major_risks) <= 2 else "Low"

    risk_tags: list[RiskTag] = []
    if ctx.top_concentration_pct >= 70:
        risk_tags.append(RiskTag(name="Concentration Risk", level="High", note=f"Top concentration is {ctx.top_concentration_pct:.1f}%"))
    elif ctx.top_concentration_pct > 0:
        risk_tags.append(RiskTag(name="Concentration Risk", level="Medium", note=f"Top concentration is {ctx.top_concentration_pct:.1f}%"))

    if ctx.notable_exposures:
        risk_tags.append(RiskTag(name="Narrative Risk", level="Medium", note=", ".join(ctx.notable_exposures)))

    if ctx.top_concentration_pct >= 75:
        quick_verdict = "This wallet is informative but heavily concentrated, which means copying it blindly would be much riskier than simply studying its behavior."
    elif ctx.top_concentration_pct >= 50:
        quick_verdict = "This wallet is worth tracking because it has visible size and recognizable exposures, but concentration still limits how clean the signal is."
    elif quality == "Medium":
        quick_verdict = "This wallet looks reasonably useful for pattern-reading because the positioning is visible without being excessively concentrated."
    else:
        quick_verdict = "This wallet has some readable structure, but the edge still comes more from watching behavior over time than from one static snapshot."

    top_risks = list(ctx.major_risks)
    if not top_risks:
        if ctx.top_concentration_pct >= 60:
            top_risks.append("High concentration can turn one bad position into a large portfolio hit.")
        if not ctx.top_holdings:
            top_risks.append("Top holding detail is too thin to judge intent confidently.")
        if not top_risks:
            top_risks.append("Wallet behavior needs repeated observation before it deserves strong smart-money claims.")

    return AnalysisBrief(
        entity=f"Wallet: {ctx.address}",
        quick_verdict=quick_verdict,
        signal_quality=quality,
        top_risks=top_risks,
        why_it_matters=_wallet_why_it_matters(ctx),
        what_to_watch_next=_wallet_watch_next(ctx),
        risk_tags=risk_tags,
        conviction=conviction,
        beginner_note="A big wallet is not automatically a smart wallet. The useful signal is in behavior, concentration, and timing.",
    )
