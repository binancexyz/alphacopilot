from __future__ import annotations

from src.models.schemas import AnalysisBrief, RiskTag
from src.services.factory import get_market_data_service
from src.services.normalizers import normalize_token_context


def analyze_price(symbol: str) -> AnalysisBrief:
    service = get_market_data_service()
    raw_context = service.get_token_context(symbol)
    ctx = normalize_token_context(raw_context)

    price_value = f"${ctx.price:,.2f}" if ctx.price > 0 else "Price unavailable"
    liquidity_note = (
        f"Liquidity context is visible at roughly ${ctx.liquidity:,.0f}." if ctx.liquidity > 0 else "Liquidity context is missing or weak."
    )

    if ctx.price > 0 and ctx.liquidity > 0:
        quick_verdict = f"{ctx.display_name} price is available and usable right now, with enough surrounding context to make a quick market check meaningful."
        quality = "High"
        conviction = "Medium"
    elif ctx.price > 0:
        quick_verdict = f"{ctx.display_name} price is available, but supporting market context is still thinner than ideal."
        quality = "Medium"
        conviction = "Low"
    else:
        quick_verdict = f"{ctx.display_name} does not currently have reliable price detail in this brief, so treat any quick read cautiously."
        quality = "Low"
        conviction = "Low"

    top_risks = []
    if ctx.price <= 0:
        top_risks.append("Price data is missing or not clean enough to trust fully.")
    if ctx.liquidity <= 0:
        top_risks.append("Liquidity context is limited, which weakens a simple price read.")
    if not top_risks:
        top_risks.append("A visible price alone does not tell you whether the setup is strong, crowded, or weakening.")

    why_it_matters = f"Current price: {price_value}. {liquidity_note}"
    if ctx.market_rank_context:
        why_it_matters += f" {ctx.market_rank_context}"

    what_to_watch_next = [
        "whether price context stays available and consistent",
        "whether liquidity remains supportive around the current level",
        "whether the token setup strengthens or weakens beyond the raw price print",
    ]

    risk_tags: list[RiskTag] = []
    risk_tags.append(RiskTag(name="Price Confidence", level="Low" if ctx.price > 0 else "High", note=price_value))
    risk_tags.append(
        RiskTag(
            name="Liquidity Context",
            level="Low" if ctx.liquidity > 0 else "Medium",
            note=f"~${ctx.liquidity:,.0f} liquidity" if ctx.liquidity > 0 else "Liquidity detail unavailable",
        )
    )

    return AnalysisBrief(
        entity=f"Price: {ctx.symbol}",
        quick_verdict=quick_verdict,
        signal_quality=quality,
        top_risks=top_risks,
        why_it_matters=why_it_matters,
        what_to_watch_next=what_to_watch_next,
        risk_tags=risk_tags,
        conviction=conviction,
        beginner_note="Price is only one layer of the story. Context, liquidity, and risk still matter.",
    )
