from __future__ import annotations

from src.models.context import SignalContext, TokenContext, WalletContext, WalletHolding, WatchTodayContext


def normalize_token_context(payload: dict) -> TokenContext:
    return TokenContext(
        symbol=payload.get("symbol", "UNKNOWN"),
        display_name=payload.get("display_name", payload.get("symbol", "UNKNOWN")),
        price=float(payload.get("price", 0.0) or 0.0),
        liquidity=float(payload.get("liquidity", 0.0) or 0.0),
        holders=int(payload.get("holders", 0) or 0),
        market_rank_context=payload.get("market_rank_context", ""),
        signal_status=payload.get("signal_status", "unknown"),
        signal_trigger_context=payload.get("signal_trigger_context", ""),
        audit_flags=list(payload.get("audit_flags", [])),
        major_risks=list(payload.get("major_risks", [])),
    )


def normalize_wallet_context(payload: dict) -> WalletContext:
    holdings = [
        WalletHolding(symbol=item.get("symbol", "UNKNOWN"), weight_pct=float(item.get("weight_pct", 0.0) or 0.0))
        for item in payload.get("top_holdings", [])
    ]
    return WalletContext(
        address=payload.get("address", ""),
        portfolio_value=float(payload.get("portfolio_value", 0.0) or 0.0),
        holdings_count=int(payload.get("holdings_count", 0) or 0),
        top_holdings=holdings,
        top_concentration_pct=float(payload.get("top_concentration_pct", 0.0) or 0.0),
        change_24h=float(payload.get("change_24h", 0.0) or 0.0),
        notable_exposures=list(payload.get("notable_exposures", [])),
        major_risks=list(payload.get("major_risks", [])),
    )


def normalize_watch_today_context(payload: dict) -> WatchTodayContext:
    return WatchTodayContext(
        top_narratives=list(payload.get("top_narratives", [])),
        strongest_signals=list(payload.get("strongest_signals", [])),
        risk_zones=list(payload.get("risk_zones", [])),
        market_takeaway=payload.get("market_takeaway", ""),
        major_risks=list(payload.get("major_risks", [])),
    )


def normalize_signal_context(payload: dict) -> SignalContext:
    return SignalContext(
        token=payload.get("token", "UNKNOWN"),
        signal_status=payload.get("signal_status", "unknown"),
        trigger_price=float(payload.get("trigger_price", 0.0) or 0.0),
        current_price=float(payload.get("current_price", 0.0) or 0.0),
        max_gain=float(payload.get("max_gain", 0.0) or 0.0),
        exit_rate=float(payload.get("exit_rate", 0.0) or 0.0),
        audit_flags=list(payload.get("audit_flags", [])),
        supporting_context=payload.get("supporting_context", ""),
        major_risks=list(payload.get("major_risks", [])),
    )
