from __future__ import annotations

from src.analyzers.price_analysis import _fetch_market_quote
from src.analyzers.token_live_brief import build_token_brief
from src.models.schemas import AnalysisBrief, RiskTag
from src.services.factory import get_market_data_service
from src.services.normalizers import normalize_token_context


def analyze_token(symbol: str) -> AnalysisBrief:
    service = get_market_data_service()
    raw_context = service.get_token_context(symbol)
    token_context = normalize_token_context(raw_context)
    brief = build_token_brief(token_context)

    try:
        quote, source = _fetch_market_quote(symbol)
    except Exception:
        quote, source = None, ""

    if quote and source == "Binance Spot":
        pair = str(quote.get("exchange_symbol") or symbol)
        spread = float(quote.get("spread_pct") or 0)
        change = float(quote.get("percent_change_24h") or 0)
        note = f"{pair} | 24h {change:+.2f}%"
        if spread > 0:
            note += f" | spread {spread:.2f}%"
        brief.risk_tags.insert(1, RiskTag(name="Binance Spot", level="Low" if spread < 0.5 else "Medium", note=note))
        if spread >= 0.5:
            brief.top_risks.insert(0, f"Binance Spot spread is relatively wide at {spread:.2f}%, so exchange execution context is less clean than the headline move suggests.")
        elif token_context.signal_status == "unmatched":
            brief.top_risks.insert(0, f"Binance Spot price is live via {pair}, but there is still no matched smart-money signal on the board.")
        elif brief.why_it_matters:
            brief.why_it_matters += f" Binance Spot confirms active pricing on {pair} with a {change:+.2f}% 24h move."

    return brief
