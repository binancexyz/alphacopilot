from __future__ import annotations

from src.analyzers.price_analysis import _fetch_market_quote
from src.analyzers.watchtoday_live_brief import build_watchtoday_brief
from src.models.schemas import AnalysisBrief
from src.services.factory import get_market_data_service
from src.services.normalizers import normalize_watch_today_context


def _build_exchange_board(symbols: list[str]) -> list[str]:
    rows: list[str] = []
    for symbol in symbols:
        try:
            quote, source = _fetch_market_quote(symbol)
        except Exception:
            quote, source = None, ""
        if not quote or source != "Binance Spot":
            continue
        change = float(quote.get("percent_change_24h") or 0)
        spread = float(quote.get("spread_pct") or 0)
        pair = str(quote.get("exchange_symbol") or symbol)
        direction = "strong" if change >= 2 else "soft" if change <= -1 else "mixed"
        line = f"{symbol} {change:+.2f}% | {pair} | {direction}"
        if spread > 0:
            line += f" | spread {spread:.2f}%"
        rows.append(line)
    return rows[:3]


def watch_today() -> AnalysisBrief:
    service = get_market_data_service()
    raw_context = service.get_watch_today_context()
    raw_context = dict(raw_context)
    if not raw_context.get("exchange_board"):
        exchange_board = _build_exchange_board(["BNB", "BTC", "SOL"])
        if exchange_board:
            raw_context["exchange_board"] = exchange_board
            if not raw_context.get("market_takeaway"):
                raw_context["market_takeaway"] = "Exchange board is populated from Binance Spot, but setup quality still depends on lane confirmation."
    watch_context = normalize_watch_today_context(raw_context)
    return build_watchtoday_brief(watch_context)
