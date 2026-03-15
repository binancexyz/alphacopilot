from __future__ import annotations

from src.analyzers.posture_context import load_portfolio_posture, posture_watchtoday_note
from src.analyzers.price_analysis import _fetch_market_quote
from src.analyzers.watchtoday_live_brief import build_watchtoday_brief
from src.models.schemas import AnalysisBrief, RiskTag
from src.services.factory import get_market_data_service
from src.services.normalizers import normalize_watch_today_context
from src.services.snapshot_history import describe_snapshot_delta, save_snapshot


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
    return rows[:10]


def watch_today() -> AnalysisBrief:
    service = get_market_data_service()
    raw_context = service.get_watch_today_context()
    raw_context = dict(raw_context)
    if not raw_context.get("exchange_board"):
        exchange_board = _build_exchange_board(["BNB", "BTC", "SOL", "ETH", "DOGE", "XRP", "ADA", "AVAX", "LINK", "TON"])
        if exchange_board:
            raw_context["exchange_board"] = exchange_board
            if not raw_context.get("market_takeaway"):
                raw_context["market_takeaway"] = "Exchange board is populated from Binance Spot, but setup quality still depends on lane confirmation."

    # Enrich with BTC 24h change for market regime detection
    if not raw_context.get("btc_change_24h"):
        try:
            btc_quote, btc_source = _fetch_market_quote("BTC")
            if btc_quote and btc_source == "Binance Spot":
                raw_context["btc_change_24h"] = float(btc_quote.get("percent_change_24h") or 0)
        except Exception:
            pass
    portfolio = load_portfolio_posture()
    posture_note = posture_watchtoday_note(portfolio)
    if posture_note:
        takeaway = str(raw_context.get("market_takeaway") or "").strip()
        raw_context["market_takeaway"] = f"{takeaway} {posture_note}".strip() if takeaway else posture_note
    watch_context = normalize_watch_today_context(raw_context)
    brief = build_watchtoday_brief(watch_context)

    # Historical delta tracking
    snapshot_data = {
        "signal_count": len(watch_context.strongest_signals),
        "market_regime": raw_context.get("market_regime", ""),
        "signal_quality": brief.signal_quality,
    }
    try:
        delta_summary, delta_watch = describe_snapshot_delta("watchtoday", "", snapshot_data)
        if delta_summary:
            brief.risk_tags.append(RiskTag(name="Board Delta", level="Info", note=delta_summary))
        if delta_watch:
            brief.what_to_watch_next = delta_watch[:1] + brief.what_to_watch_next[:3]
        save_snapshot("watchtoday", "", snapshot_data)
    except Exception:
        pass

    return brief
