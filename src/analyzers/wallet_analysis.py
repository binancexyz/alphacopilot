from __future__ import annotations

from src.analyzers.wallet_live_brief import build_wallet_brief
from src.models.schemas import AnalysisBrief, RiskTag
from src.services.factory import get_market_data_service
from src.services.normalizers import normalize_wallet_context


def analyze_wallet(address: str) -> AnalysisBrief:
    service = get_market_data_service()
    raw_context = service.get_wallet_context(address)
    wallet_context = normalize_wallet_context(raw_context)
    brief = build_wallet_brief(wallet_context)

    if wallet_context.top_holdings:
        top = wallet_context.top_holdings[0]
        brief.risk_tags.insert(1, RiskTag(name="Lead Holding", level="Medium", note=f"{top.symbol} {top.weight_pct:.1f}%"))
        if wallet_context.holdings_count >= 5 and wallet_context.top_concentration_pct < 60 and wallet_context.follow_verdict == "Track":
            brief.why_it_matters += f" The visible spread across {wallet_context.holdings_count} holdings makes this more useful for public posture study than a one-bet wallet."
        if brief.beginner_note:
            brief.beginner_note += " Think of /wallet as public posture, while /portfolio is your private Binance Spot posture."
    return brief
