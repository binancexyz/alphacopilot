from __future__ import annotations

from src.models.context import SignalContext, TokenContext, WalletContext, WatchTodayContext


def token_signal_quality(ctx: TokenContext) -> str:
    score = 0
    if ctx.liquidity > 0:
        score += 1
    if ctx.holders > 0:
        score += 1
    if ctx.signal_status in {"watch", "bullish", "triggered"}:
        score += 1
    if not ctx.audit_flags:
        score += 1

    if score >= 4:
        return "High"
    if score >= 2:
        return "Medium"
    return "Low"


def token_conviction(ctx: TokenContext) -> str:
    quality = token_signal_quality(ctx)
    risk_count = len(ctx.major_risks) + len(ctx.audit_flags)
    if quality == "High" and risk_count <= 1:
        return "High"
    if quality in {"High", "Medium"} and risk_count <= 3:
        return "Medium"
    return "Low"


def signal_quality_from_signal(ctx: SignalContext) -> str:
    if ctx.signal_status in {"triggered", "bullish"} and not ctx.audit_flags:
        return "High"
    if ctx.signal_status in {"watch", "triggered", "bullish"}:
        return "Medium"
    return "Low"


def wallet_signal_quality(ctx: WalletContext) -> str:
    score = 0
    if ctx.portfolio_value > 0:
        score += 1
    if ctx.holdings_count >= 5:
        score += 1
    if ctx.top_holdings:
        score += 1
    if ctx.change_24h != 0:
        score += 1

    concentration = ctx.top_concentration_pct
    if concentration >= 80:
        score -= 2
    elif concentration >= 65:
        score -= 1

    if score >= 3:
        return "Medium"
    if score >= 1:
        return "Low"
    return "Low"


def watch_today_signal_quality(ctx: WatchTodayContext) -> str:
    if len(ctx.top_narratives) >= 3 and len(ctx.strongest_signals) >= 2:
        return "High"
    if ctx.top_narratives or ctx.strongest_signals:
        return "Medium"
    return "Low"
