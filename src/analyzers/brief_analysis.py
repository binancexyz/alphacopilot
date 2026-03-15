from __future__ import annotations

from src.analyzers.judgment_helpers import portfolio_note_for
from src.analyzers.price_analysis import _fetch_market_quote
from src.services.factory import get_market_data_service
from src.services.normalizers import normalize_signal_context, normalize_token_context
from src.models.schemas import AnalysisBrief, RiskTag
from src.formatters.brief_formatter import _human_money

_NATIVE_CONTRACTS = {"0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee", "0x0000000000000000000000000000000000000000"}


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

    audit_gate = str(token_raw.get("audit_gate") or "")
    audit_blocked = audit_gate == "BLOCK"
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

    signal_quality = "High" if signal.signal_status in {"triggered", "bullish"} else "Medium" if signal.signal_status in {"watch", "active"} else "Low"
    if signal.signal_status == "active" and signal.smart_money_count >= 3:
        signal_quality = "High"
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

    if audit_blocked:
        verdict = "Blocked. Audit risk too high."
        signal_quality = "Low"
    elif signal_quality == "High" and not token.audit_flags:
        verdict = "Conviction setup. Follow-through still needed."
    elif signal_quality == "High" and token.audit_flags:
        verdict = "Signal is strong, but audit flags cap conviction."
        signal_quality = "Medium"
    elif signal_quality == "Medium" and quote_source == "Binance Spot" and spread_pct <= 0.2:
        verdict = "Clean price context. Setup needs confirmation."
    elif signal_quality == "Medium":
        verdict = "Watch setup. Not clean enough yet."
    else:
        verdict = "Monitor only. No conviction setup."

    portfolio_note = portfolio_note_for(display_symbol)
    if portfolio_note:
        top_risk = f"{top_risk} {portfolio_note}".strip()

    volume_24h = float(quote.get("volume_24h") or token.volume_24h or 0) if quote else token.volume_24h
    market_cap = float(quote.get("market_cap") or token.market_cap or 0) if quote else token.market_cap
    why = (
        f"{display_name}|{display_symbol}|{price}|{change}|{rank}|{signal.signal_status}|{token.liquidity}|{top_risk}|{verdict}|"
        f"{volume_24h}|{market_cap}|{signal.smart_money_count}|{token.kline_trend}"
    )

    tags: list[RiskTag] = []
    if audit_blocked:
        tags.append(RiskTag(name="Audit Gate", level="High", note=str(token_raw.get("blocked_reason") or "Blocked by live audit")))
    elif token.audit_flags:
        tags.append(RiskTag(name="Audit Gate", level="Medium", note=", ".join(token.audit_flags[:2])))
    if quote_source:
        level = "Low" if quote_source == "Binance Spot" else "Info"
        tags.append(RiskTag(name="Source", level=level, note=quote_source if quote_source == "Binance Spot" else "Secondary market data"))

    if volume_24h > 0:
        tags.append(RiskTag(name="Volume 24h", level="Info", note=_human_money(volume_24h)))
    if market_cap > 0:
        tags.append(RiskTag(name="Market Cap", level="Info", note=_human_money(market_cap)))
    if signal.smart_money_count > 0:
        tags.append(RiskTag(name="Smart Money", level="Info", note=f"{signal.smart_money_count} wallet{'s' if signal.smart_money_count != 1 else ''}"))
    if token.holders > 0:
        tags.append(RiskTag(name="Holders", level="Info", note=f"{token.holders:,}"))
    if token.top_holder_concentration_pct > 0:
        tags.append(RiskTag(name="Ownership", level="Info", note=f"Top-10 concentration {token.top_holder_concentration_pct:.1f}%"))
    if token.smart_money_holders > 0:
        tags.append(RiskTag(name="Smart Money Holders", level="Info", note=f"{token.smart_money_holders}"))
    if token.smart_money_holding_pct > 0:
        tags.append(RiskTag(name="Smart Money Holding %", level="Info", note=f"{token.smart_money_holding_pct:.1f}%"))
    if token.kline_trend:
        tags.append(RiskTag(name="K-line", level="Info", note=token.kline_trend))

    if quote_source == "Binance Spot" and exchange_symbol:
        spot_note = exchange_symbol
        if spread_pct > 0:
            spot_note += f" | spread {spread_pct:.2f}%"
        tags.append(RiskTag(name="Binance Spot", level="Low", note=spot_note))
        bid_qty = float(quote.get("bid_qty") or 0)
        ask_qty = float(quote.get("ask_qty") or 0)
        trading_days = quote.get("trading_days")

        if bid_qty > 0 and ask_qty > 0:
            if bid_qty > ask_qty * 3:
                tags.append(RiskTag(name="Order Book", level="Low", note="Bid depth significantly outweighs ask depth (3x+)"))
            elif ask_qty > bid_qty * 3:
                tags.append(RiskTag(name="Order Book", level="Medium", note="Ask depth significantly outweighs bid depth (3x+)"))

        if trading_days is not None:
            if trading_days <= 14:
                tags.append(RiskTag(name="Maturity", level="High", note=f"Very fresh market ({trading_days} days of history)"))
            elif trading_days >= 365:
                tags.append(RiskTag(name="Maturity", level="Low", note=f"Vintage market ({trading_days}+ days)"))

    return AnalysisBrief(
        entity=f"Brief: {display_symbol}",
        quick_verdict=why,
        signal_quality=signal_quality if quote_source == "Binance Spot" or signal_quality != "High" else "Medium",
        top_risks=[],
        why_it_matters="",
        what_to_watch_next=[],
        risk_tags=tags,
        conviction=None,
        beginner_note=None,
    )
