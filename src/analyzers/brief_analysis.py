from __future__ import annotations

from src.analyzers.judgment_helpers import portfolio_note_for
from src.analyzers.price_analysis import _fetch_market_quote
from src.services.factory import get_market_data_service
from src.services.normalizers import normalize_signal_context, normalize_token_context
from src.models.schemas import AnalysisBrief, RiskTag


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
    spread_pct = 0.0
    exchange_symbol = ""
    if quote:
        price = float(quote.get("price") or 0)
        change = float(quote.get("percent_change_24h") or 0)
        rank = int(quote.get("rank") or 0)
        spread_pct = float(quote.get("spread_pct") or 0)
        exchange_symbol = str(quote.get("exchange_symbol") or "")
    elif token.price > 0:
        price = token.price

    if not price and token.price > 0:
        price = token.price

    display_name, display_symbol = _preferred_identity(symbol, token.display_name, token.symbol, quote)

    signal_quality = "High" if signal.signal_status in {"triggered", "bullish"} else "Medium" if signal.signal_status in {"watch"} else "Low"
    top_risk = token.major_risks[0] if token.major_risks else signal.major_risks[0] if signal.major_risks else "Context is still incomplete, so treat this as a monitor-first setup."

    if not price and not quote:
        top_risk = "Live market quote temporarily unavailable, so this brief is using thinner fallback context."
    elif quote_source == "Binance Spot":
        if spread_pct >= 0.5:
            top_risk = f"Binance Spot spread is relatively wide at {spread_pct:.2f}%, so execution quality may be less clean than the headline price suggests."
        elif signal.signal_status == "unmatched":
            top_risk = f"Binance Spot price is live through {exchange_symbol or display_symbol}, but there is still no matched live smart-money signal on the board."
        else:
            top_risk = f"Using Binance Spot market data via {exchange_symbol or display_symbol}; exchange price context is good, but setup quality still depends on confirmation."
    elif quote and quote_source and quote_source != "Binance Spot":
        top_risk = "Using secondary market data for this brief."

    if signal_quality == "High" and not token.audit_flags:
        verdict = "Looks constructive, but still needs follow-through."
    elif signal_quality == "Medium" and quote_source == "Binance Spot" and spread_pct <= 0.2:
        verdict = "Worth watching; exchange price context looks clean enough, but setup quality still needs proof."
    elif signal_quality == "Medium":
        verdict = "Worth watching, but not clean enough to trust blindly."
    else:
        verdict = "More of a monitor than a conviction setup right now."

    portfolio_note = portfolio_note_for(display_symbol)
    if portfolio_note:
        top_risk = f"{top_risk} {portfolio_note}".strip()

    why = f"{display_name}|{display_symbol}|{price}|{change}|{rank}|{signal.signal_status}|{token.liquidity}|{top_risk}|{verdict}"

    tags: list[RiskTag] = []
    if quote_source:
        level = "Low" if quote_source == "Binance Spot" else "Info"
        tags.append(RiskTag(name="Source", level=level, note=quote_source if quote_source == "Binance Spot" else "Secondary market data"))
    if quote_source == "Binance Spot" and exchange_symbol:
        tags.append(RiskTag(name="Binance Spot", level="Low", note=exchange_symbol))

    return AnalysisBrief(
        entity=f"Brief: {display_symbol}",
        quick_verdict=why,
        signal_quality="High" if quote_source == "Binance Spot" and signal_quality == "High" else signal_quality,
        top_risks=[],
        why_it_matters="",
        what_to_watch_next=[],
        risk_tags=tags,
        conviction=None,
        beginner_note=None,
    )
