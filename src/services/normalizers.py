from __future__ import annotations

from src.models.context import MemeContext, SignalContext, TokenContext, WalletContext, WalletHolding, WatchTodayContext
from src.utils.converters import safe_float as _to_float, safe_int as _to_int


def normalize_token_context(payload: dict) -> TokenContext:
    return TokenContext(
        symbol=str(payload.get("symbol", "UNKNOWN")),
        display_name=str(payload.get("display_name", payload.get("symbol", "UNKNOWN"))),
        price=_to_float(payload.get("price")),
        liquidity=_to_float(payload.get("liquidity")),
        holders=_to_int(payload.get("holders")),
        volume_24h=_to_float(payload.get("volume_24h")),
        pct_change_24h=_to_float(payload.get("pct_change_24h")),
        market_cap=_to_float(payload.get("market_cap")),
        top_holder_concentration_pct=_to_float(payload.get("top_holder_concentration_pct")),
        market_rank_context=str(payload.get("market_rank_context", "")),
        signal_status=str(payload.get("signal_status", "unknown")),
        signal_trigger_context=str(payload.get("signal_trigger_context", "")),
        audit_flags=[str(x) for x in payload.get("audit_flags", [])],
        major_risks=[str(x) for x in payload.get("major_risks", [])],
        smart_money_count=_to_int(payload.get("smart_money_count")),
        smart_money_holders=_to_int(payload.get("smart_money_holders")),
        smart_money_holding_pct=_to_float(payload.get("smart_money_holding_pct")),
        smart_money_inflow_usd=_to_float(payload.get("smart_money_inflow_usd")),
        smart_money_inflow_traders=_to_int(payload.get("smart_money_inflow_traders")),
        exit_rate=_to_float(payload.get("exit_rate")),
        signal_age_hours=_to_float(payload.get("signal_age_hours")),
        signal_freshness=str(payload.get("signal_freshness", "UNKNOWN")),
        audit_gate=str(payload.get("audit_gate", "ALLOW")),
        blocked_reason=str(payload.get("blocked_reason", "")),
        futures_funding_rate=_to_float(payload.get("futures_funding_rate")),
        futures_long_short_ratio=_to_float(payload.get("futures_long_short_ratio")),
        futures_sentiment=str(payload.get("futures_sentiment", "")),
        meme_lifecycle=str(payload.get("meme_lifecycle", "")),
        meme_bonded_progress=_to_float(payload.get("meme_bonded_progress")),
        is_meme_candidate=bool(payload.get("is_meme_candidate", False)),
        kline_trend=str(payload.get("kline_trend", "")),
        kline_above_ma20=bool(payload.get("kline_above_ma20", False)),
        top_trader_interest=bool(payload.get("top_trader_interest", False)),
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
        volatility_24h=_to_float(payload.get("volatility_24h")),
        notable_exposures=[str(x) for x in payload.get("notable_exposures", [])],
        major_risks=[str(x) for x in payload.get("major_risks", [])],
        follow_verdict=str(payload.get("follow_verdict", "Unknown")),
        style_read=str(payload.get("style_read", "")),
        style_profile=str(payload.get("style_profile", "")),
        exposure_breakdown=[str(x) for x in payload.get("exposure_breakdown", [])],
        risky_holdings_count=_to_int(payload.get("risky_holdings_count")),
        holdings_audit_notes=[str(x) for x in payload.get("holdings_audit_notes", [])],
    )


def normalize_watch_today_context(payload: dict) -> WatchTodayContext:
    return WatchTodayContext(
        top_narratives=[str(x) for x in payload.get("top_narratives", [])],
        strongest_signals=[str(x) for x in payload.get("strongest_signals", [])],
        risk_zones=[str(x) for x in payload.get("risk_zones", [])],
        market_takeaway=str(payload.get("market_takeaway", "")),
        major_risks=[str(x) for x in payload.get("major_risks", [])],
        trending_now=[str(x) for x in payload.get("trending_now", [])],
        smart_money_flow=[str(x) for x in payload.get("smart_money_flow", [])],
        social_hype=[str(x) for x in payload.get("social_hype", [])],
        meme_watch=[str(x) for x in payload.get("meme_watch", [])],
        top_picks=[str(x) for x in payload.get("top_picks", [])],
        exchange_board=[str(x) for x in payload.get("exchange_board", [])],
    )


def normalize_signal_context(payload: dict) -> SignalContext:
    return SignalContext(
        token=str(payload.get("token", "UNKNOWN")),
        signal_status=str(payload.get("signal_status", "unknown")),
        trigger_price=_to_float(payload.get("trigger_price")),
        current_price=_to_float(payload.get("current_price")),
        max_gain=_to_float(payload.get("max_gain")),
        exit_rate=_to_float(payload.get("exit_rate")),
        liquidity=_to_float(payload.get("liquidity")),
        holders=_to_int(payload.get("holders")),
        volume_24h=_to_float(payload.get("volume_24h")),
        pct_change_24h=_to_float(payload.get("pct_change_24h")),
        market_cap=_to_float(payload.get("market_cap")),
        audit_flags=[str(x) for x in payload.get("audit_flags", [])],
        supporting_context=str(payload.get("supporting_context", "")),
        major_risks=[str(x) for x in payload.get("major_risks", [])],
        smart_money_count=_to_int(payload.get("smart_money_count")),
        smart_money_holders=_to_int(payload.get("smart_money_holders")),
        smart_money_holding_pct=_to_float(payload.get("smart_money_holding_pct")),
        smart_money_inflow_usd=_to_float(payload.get("smart_money_inflow_usd")),
        signal_age_hours=_to_float(payload.get("signal_age_hours")),
        signal_freshness=str(payload.get("signal_freshness", "UNKNOWN")),
        audit_gate=str(payload.get("audit_gate", "ALLOW")),
        blocked_reason=str(payload.get("blocked_reason", "")),
        funding_rate=_to_float(payload.get("funding_rate")),
        long_short_ratio=_to_float(payload.get("long_short_ratio")),
        funding_sentiment=str(payload.get("funding_sentiment", "")),
    )


def normalize_meme_context(payload: dict) -> MemeContext:
    return MemeContext(
        symbol=str(payload.get("symbol", "UNKNOWN")),
        display_name=str(payload.get("display_name", payload.get("symbol", "UNKNOWN"))),
        price=_to_float(payload.get("price")),
        liquidity=_to_float(payload.get("liquidity")),
        market_rank_context=str(payload.get("market_rank_context", "")),
        signal_status=str(payload.get("signal_status", "unknown")),
        audit_flags=[str(x) for x in payload.get("audit_flags", [])],
        major_risks=[str(x) for x in payload.get("major_risks", [])],
        smart_money_count=_to_int(payload.get("smart_money_count")),
        exit_rate=_to_float(payload.get("exit_rate")),
        signal_age_hours=_to_float(payload.get("signal_age_hours")),
        signal_freshness=str(payload.get("signal_freshness", "UNKNOWN")),
        audit_gate=str(payload.get("audit_gate", "ALLOW")),
        blocked_reason=str(payload.get("blocked_reason", "")),
        launch_platform=str(payload.get("launch_platform", "")),
        is_alpha=bool(payload.get("is_alpha", False)),
        lifecycle_stage=str(payload.get("lifecycle_stage", "unknown")),
        bonded_progress=_to_float(payload.get("bonded_progress")),
        meme_score=_to_float(payload.get("meme_score")),
        social_brief=str(payload.get("social_brief", "")),
        top_holder_concentration_pct=_to_float(payload.get("top_holder_concentration_pct")),
    )

