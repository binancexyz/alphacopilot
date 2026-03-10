from __future__ import annotations

from src.models.context import SignalContext, TokenContext, WalletContext, WalletHolding, WatchTodayContext


def normalize_token_context(payload: dict) -> TokenContext:
    return TokenContext(
        symbol=str(payload.get("symbol", "UNKNOWN")),
        display_name=str(payload.get("display_name", payload.get("symbol", "UNKNOWN"))),
        price=_to_float(payload.get("price")),
        liquidity=_to_float(payload.get("liquidity")),
        holders=_to_int(payload.get("holders")),
        market_rank_context=str(payload.get("market_rank_context", "")),
        signal_status=str(payload.get("signal_status", "unknown")),
        signal_trigger_context=str(payload.get("signal_trigger_context", "")),
        audit_flags=[str(x) for x in payload.get("audit_flags", [])],
        major_risks=[str(x) for x in payload.get("major_risks", [])],
    )


def normalize_wallet_context(payload: dict) -> WalletContext:
    holdings = [
        WalletHolding(symbol=str(item.get("symbol", "UNKNOWN")), weight_pct=_to_float(item.get("weight_pct")))
        for item in payload.get("top_holdings", [])
    ]
    return WalletContext(
        address=str(payload.get("address", "")),
        portfolio_value=_to_float(payload.get("portfolio_value")),
        holdings_count=_to_int(payload.get("holdings_count")),
        top_holdings=holdings,
        top_concentration_pct=_to_float(payload.get("top_concentration_pct")),
        change_24h=_to_float(payload.get("change_24h")),
        notable_exposures=[str(x) for x in payload.get("notable_exposures", [])],
        major_risks=[str(x) for x in payload.get("major_risks", [])],
    )


def normalize_watch_today_context(payload: dict) -> WatchTodayContext:
    return WatchTodayContext(
        top_narratives=[str(x) for x in payload.get("top_narratives", [])],
        strongest_signals=[str(x) for x in payload.get("strongest_signals", [])],
        risk_zones=[str(x) for x in payload.get("risk_zones", [])],
        market_takeaway=str(payload.get("market_takeaway", "")),
        major_risks=[str(x) for x in payload.get("major_risks", [])],
    )


def normalize_signal_context(payload: dict) -> SignalContext:
    return SignalContext(
        token=str(payload.get("token", "UNKNOWN")),
        signal_status=str(payload.get("signal_status", "unknown")),
        trigger_price=_to_float(payload.get("trigger_price")),
        current_price=_to_float(payload.get("current_price")),
        max_gain=_to_float(payload.get("max_gain")),
        exit_rate=_to_float(payload.get("exit_rate")),
        audit_flags=[str(x) for x in payload.get("audit_flags", [])],
        supporting_context=str(payload.get("supporting_context", "")),
        major_risks=[str(x) for x in payload.get("major_risks", [])],
    )


def _to_float(value) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _to_int(value) -> int:
    try:
        return int(float(value or 0))
    except (TypeError, ValueError):
        return 0
