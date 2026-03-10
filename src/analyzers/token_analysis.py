from __future__ import annotations

from src.formatters.conviction import conviction_label
from src.models.schemas import AnalysisBrief, RiskTag
from src.services.factory import get_market_data_service


def analyze_token(symbol: str) -> AnalysisBrief:
    service = get_market_data_service()
    context = service.get_token_context(symbol)
    risk_tags = [
        RiskTag(name="Narrative Risk", level="Medium", note="Attention may fade without follow-through."),
        RiskTag(name="Liquidity Risk", level="Low", note="No immediate liquidity concern assumed in scaffold mode."),
    ]
    brief = AnalysisBrief(
        entity=f"Token: {symbol}",
        quick_verdict=context.get("quick_context", f"{symbol} looks worth monitoring, but conviction still depends on confirmation and risk balance."),
        signal_quality=f"{context.get('signal_quality', 'Medium')} — early positive context, but not enough evidence yet for high conviction.",
        top_risks=context.get("risks", []),
        why_it_matters=f"{symbol} may have useful signal value, but users need context on both upside and fragility rather than raw hype.",
        what_to_watch_next=[
            "volume follow-through",
            "signal persistence across the next cycle",
            "whether risk flags stay stable or worsen",
        ],
        risk_tags=risk_tags,
    )
    brief.conviction = conviction_label(brief.signal_quality, len(brief.top_risks))
    brief.beginner_note = "This is a research summary, not a buy/sell instruction."
    return brief
