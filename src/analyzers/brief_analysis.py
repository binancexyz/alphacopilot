from __future__ import annotations

from src.analyzers.price_analysis import _fetch_market_quote
from src.services.factory import get_market_data_service
from src.services.normalizers import normalize_signal_context, normalize_token_context
from src.models.schemas import AnalysisBrief


_MAJOR_SYMBOLS = {"BTC", "ETH", "BNB", "SOL", "XRP", "DOGE", "ADA", "TRX", "TON", "AVAX", "LINK"}


def _preferred_identity(requested_symbol: str, token_name: str, token_symbol: str, quote: dict | None) -> tuple[str, str]:
    requested = requested_symbol.upper()
    if quote and requested in _MAJOR_SYMBOLS:
        return str(quote.get("name") or token_name), str(quote.get("symbol") or requested)
    return token_name, token_symbol


def analyze_brief(symbol: str) -> AnalysisBrief:
    service = get_market_data_service()
    token_raw = service.get_token_context(symbol)
    signal_raw = service.get_signal_context(symbol)

    token = normalize_token_context(token_raw)
    signal = normalize_signal_context(signal_raw)
    quote, quote_source = _fetch_market_quote(symbol)

    price = 0.0
    change = 0.0
    rank = 0
    if quote:
        price = float(quote.get("price") or 0)
        change = float(quote.get("percent_change_24h") or 0)
        rank = int(quote.get("rank") or 0)
    elif token.price > 0:
        price = token.price

    if not price and token.price > 0:
        price = token.price

    display_name, display_symbol = _preferred_identity(symbol, token.display_name, token.symbol, quote)

    signal_quality = "High" if signal.signal_status in {"triggered", "bullish"} else "Medium" if signal.signal_status in {"watch"} else "Low"
    top_risk = token.major_risks[0] if token.major_risks else signal.major_risks[0] if signal.major_risks else "Context is still incomplete, so treat this as a monitor-first setup."

    if not price and not quote:
        top_risk = "Live market quote temporarily unavailable, so this brief is using thinner fallback context."
    elif quote and quote_source and quote_source != "CoinGecko":
        top_risk = f"Primary CoinGecko quote was unavailable, so this brief is using {quote_source} market data."

    if signal_quality == "High" and not token.audit_flags:
        verdict = "Looks constructive, but still needs follow-through."
    elif signal_quality == "Medium":
        verdict = "Worth watching, but not clean enough to trust blindly."
    else:
        verdict = "More of a monitor than a conviction setup right now."

    why = f"{display_name}|{display_symbol}|{price}|{change}|{rank}|{signal.signal_status}|{token.liquidity}|{top_risk}|{verdict}"

    return AnalysisBrief(
        entity=f"Brief: {display_symbol}",
        quick_verdict=why,
        signal_quality=signal_quality,
        top_risks=[],
        why_it_matters="",
        what_to_watch_next=[],
        risk_tags=[],
        conviction=None,
        beginner_note=None,
    )
