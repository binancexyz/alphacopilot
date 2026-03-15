from __future__ import annotations

from src.analyzers.thresholds import (
    CONCENTRATION_ELEVATED,
    CONCENTRATION_EXTREME,
    EXIT_RATE_HIGH,
    EXIT_RATE_MODERATE,
    LIQUIDITY_DEEP,
    LIQUIDITY_MODERATE,
    LIQUIDITY_THIN,
)
from src.formatters.heuristics import token_conviction, token_signal_quality
from src.models.context import TokenContext
from src.models.schemas import AnalysisBrief, RiskTag


def _human_money(value: float) -> str:
    abs_value = abs(value)
    if abs_value >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:.1f}T"
    if abs_value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.1f}B"
    if abs_value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    if abs_value >= 1_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:,.2f}"


def _momentum_note(ctx: TokenContext) -> str:
    parts: list[str] = []
    for label, value in (("5m", ctx.pct_change_5m), ("1h", ctx.pct_change_1h), ("4h", ctx.pct_change_4h)):
        if value != 0:
            parts.append(f"{label} {value:+.1f}%")
    return " | ".join(parts)


def _compute_momentum_score(ctx: TokenContext) -> float:
    if ctx.momentum_score != 0:
        return ctx.momentum_score
    weights = [(ctx.pct_change_5m, 0.1), (ctx.pct_change_1h, 0.25), (ctx.pct_change_4h, 0.35), (ctx.pct_change_24h, 0.3)]
    score = sum(value * weight for value, weight in weights if value != 0)
    return round(score, 2)


def _volume_trend_note(ctx: TokenContext) -> str:
    if ctx.volume_trend:
        return ctx.volume_trend
    if ctx.volume_5m <= 0 or ctx.volume_1h <= 0:
        return ""
    ratio_5m_to_1h = (ctx.volume_5m * 12) / ctx.volume_1h if ctx.volume_1h > 0 else 0
    if ratio_5m_to_1h >= 2.0:
        return "spike"
    if ratio_5m_to_1h >= 1.3:
        return "increasing"
    if ratio_5m_to_1h <= 0.5:
        return "decreasing"
    return "flat"


def _relative_strength_note(ctx: TokenContext) -> str:
    if ctx.btc_change_24h == 0 or ctx.pct_change_24h == 0:
        return ""
    relative = ctx.pct_change_24h - ctx.btc_change_24h
    if relative > 3:
        return f"Strong outperformance vs BTC (+{relative:.1f}pp)"
    if relative > 1:
        return f"Slight outperformance vs BTC (+{relative:.1f}pp)"
    if relative < -3:
        return f"Underperforming BTC ({relative:.1f}pp)"
    if relative < -1:
        return f"Slight underperformance vs BTC ({relative:.1f}pp)"
    return f"Tracking BTC ({relative:+.1f}pp)"


def _buy_sell_note(ctx: TokenContext) -> str:
    if ctx.buy_sell_ratio <= 0:
        return ""
    buy_pct = ctx.buy_sell_ratio * 100
    sell_pct = max(0.0, 100 - buy_pct)
    pressure = "buy-heavy" if ctx.buy_sell_ratio >= 0.55 else "sell-heavy" if ctx.buy_sell_ratio <= 0.45 else "balanced"
    return f"{pressure} ({buy_pct:.0f}% buy / {sell_pct:.0f}% sell)"


def _token_evidence_level(ctx: TokenContext) -> tuple[str, str]:
    score = 0
    if ctx.price > 0:
        score += 1
    if ctx.liquidity > 0:
        score += 1
    if ctx.holders > 0:
        score += 1
    if ctx.market_rank_context:
        score += 1
    if ctx.signal_status != "unknown":
        score += 1
    if ctx.signal_status == "unmatched":
        score -= 1
    if ctx.smart_money_count > 0:
        score += 1

    if score >= 5:
        return "High", "The token has enough live structure to support a more serious read."
    if score >= 3:
        return "Medium", "The token read is usable, but some important live context is still incomplete."
    return "Low", "The token read is provisional because too much of the live context is still incomplete or unmatched."


def _token_price_line(ctx: TokenContext) -> str:
    if ctx.price > 0:
        return f"{ctx.display_name} is currently trading around ${ctx.price:,.2f}, so the setup is easier to frame than a token with missing price context."
    return f"{ctx.display_name} already has enough context to analyze, but price precision is still limited in this brief."


def _token_why_it_matters(ctx: TokenContext) -> str:
    pieces: list[str] = []
    if ctx.audit_gate == "BLOCK" and ctx.blocked_reason:
        pieces.append(ctx.blocked_reason)
    if ctx.signal_trigger_context:
        pieces.append(ctx.signal_trigger_context)
    if ctx.market_rank_context and ctx.market_rank_context not in pieces:
        pieces.append(ctx.market_rank_context)
    if ctx.smart_money_count > 0:
        pieces.append(f"{ctx.smart_money_count} smart-money wallets are visible in the current setup.")
    if ctx.smart_money_inflow_usd > 0:
        pieces.append(f"Smart-money inflow is visible at roughly ${ctx.smart_money_inflow_usd:,.0f}.")
    if ctx.signal_freshness != "UNKNOWN":
        pieces.append(f"Signal timing reads as {ctx.signal_freshness.lower()} ({ctx.signal_age_hours:.1f}h old).")
    if ctx.kline_trend:
        pieces.append(f"4h K-line trend reads {ctx.kline_trend} and price is {'above' if ctx.kline_above_ma20 else 'below'} the recent MA20.")
    buy_sell_note = _buy_sell_note(ctx)
    if buy_sell_note:
        pieces.append(f"24h order flow looks {buy_sell_note}.")
    if ctx.kol_holders > 0:
        holder_note = f"KOL holders are visible at {ctx.kol_holders}"
        if ctx.kol_holding_pct > 0:
            holder_note += f" ({ctx.kol_holding_pct:.1f}%)"
        if ctx.pro_holders > 0:
            holder_note += f", with pro holders at {ctx.pro_holders}"
            if ctx.pro_holding_pct > 0:
                holder_note += f" ({ctx.pro_holding_pct:.1f}%)"
        holder_note += "."
        pieces.append(holder_note)
    momentum_note = _momentum_note(ctx)
    if momentum_note:
        pieces.append(f"Multi-timeframe momentum reads {momentum_note}.")
    if ctx.is_meme_candidate and ctx.meme_lifecycle:
        pieces.append(f"Meme lifecycle reads {ctx.meme_lifecycle} with bonding progress near {ctx.meme_bonded_progress:.0f}%.")
    if ctx.top_trader_interest:
        pieces.append("Top-trader PnL tables also show this symbol among recent top earners.")
    if not pieces:
        pieces.append(_token_price_line(ctx))
    return " ".join(pieces[:5]).strip()


def _token_watch_next(ctx: TokenContext) -> list[str]:
    watch: list[str] = []
    if ctx.audit_gate == "BLOCK":
        watch.append("do not treat the signal as actionable unless the audit picture changes materially")
        return watch

    if ctx.signal_status in {"watch", "bullish", "triggered", "active"}:
        watch.append("whether the current signal status improves from attention into real follow-through")
    else:
        watch.append("whether a clearer signal status appears instead of vague market attention")

    if ctx.exit_rate >= EXIT_RATE_HIGH:
        watch.append("whether smart-money exit pressure cools down, because the current setup already looks late")
    elif ctx.exit_rate >= EXIT_RATE_MODERATE:
        watch.append("whether exits stabilize instead of climbing into a late-signal profile")

    if ctx.signal_freshness == "STALE":
        watch.append("whether fresh confirmation appears, because the current signal timing is already stale")
    elif ctx.signal_freshness == "AGING":
        watch.append("whether the setup refreshes before timing quality degrades further")

    if ctx.liquidity > 0:
        watch.append("whether liquidity remains supportive as attention rotates")
    else:
        watch.append("whether reliable liquidity context becomes visible before conviction increases")
    return watch



def _token_state_label(ctx: TokenContext, quality: str, evidence_level: str) -> str:
    if ctx.audit_gate == "BLOCK":
        return "blocked"
    if evidence_level == "Low":
        return "thin"
    if ctx.signal_status == "unmatched":
        return "unmatched"
    if ctx.signal_freshness == "STALE":
        return "stale"
    if ctx.exit_rate >= EXIT_RATE_HIGH:
        return "late"
    if quality == "High" and ctx.smart_money_count > 0 and ctx.liquidity > 0:
        return "active"
    if quality in {"High", "Medium"} and ctx.signal_status in {"watch", "bullish", "triggered", "active"}:
        return "early"
    return "fragile"


def build_token_brief(ctx: TokenContext) -> AnalysisBrief:
    quality = token_signal_quality(ctx)
    conviction = token_conviction(ctx)
    evidence_level, evidence_note = _token_evidence_level(ctx)
    state = _token_state_label(ctx, quality, evidence_level)

    risk_tags: list[RiskTag] = [RiskTag(name="Evidence Quality", level=evidence_level, note=evidence_note)]
    gate_level = "High" if ctx.audit_gate == "BLOCK" else "Medium" if ctx.audit_gate == "WARN" else "Low"
    if ctx.audit_flags or ctx.audit_gate != "ALLOW":
        note = ctx.blocked_reason or ", ".join(ctx.audit_flags) or "Audit returned caution flags."
        risk_tags.append(RiskTag(name="Audit Gate", level=gate_level, note=note))
    if ctx.signal_freshness != "UNKNOWN":
        freshness_note = f"{ctx.signal_freshness.title()} | {ctx.signal_age_hours:.1f}h old"
        risk_tags.append(RiskTag(name="Signal Timing", level="High" if ctx.signal_freshness == "STALE" else "Medium" if ctx.signal_freshness == "AGING" else "Low", note=freshness_note))
    if ctx.exit_rate > 0:
        exit_note = f"Exit rate {ctx.exit_rate:.0f}%"
        risk_tags.append(RiskTag(name="Exit Pressure", level="High" if ctx.exit_rate >= 70 else "Medium" if ctx.exit_rate >= 40 else "Low", note=exit_note))
    if ctx.top_holder_concentration_pct > 0:
        concentration_level = "High" if ctx.top_holder_concentration_pct >= CONCENTRATION_EXTREME else "Medium" if ctx.top_holder_concentration_pct >= CONCENTRATION_ELEVATED else "Low"
        risk_tags.append(RiskTag(name="Ownership", level=concentration_level, note=f"Top-10 concentration {ctx.top_holder_concentration_pct:.1f}%"))
    if ctx.liquidity > 0:
        liquidity_level = "High" if ctx.liquidity >= LIQUIDITY_DEEP else "Medium" if ctx.liquidity >= LIQUIDITY_MODERATE else "Low"
        risk_tags.append(RiskTag(name="Liquidity", level=liquidity_level, note=f"Visible liquidity {ctx.liquidity:,.0f}"))
    market_lines: list[str] = []
    if ctx.volume_24h > 0:
        market_lines.append(f"Volume 24h: {_human_money(ctx.volume_24h)}")
    if ctx.market_cap > 0:
        market_lines.append(f"Market Cap: {_human_money(ctx.market_cap)}")
    if ctx.price_high_24h > 0 or ctx.price_low_24h > 0:
        high = f"${ctx.price_high_24h:,.2f}" if ctx.price_high_24h > 0 else "—"
        low = f"${ctx.price_low_24h:,.2f}" if ctx.price_low_24h > 0 else "—"
        market_lines.append(f"24h Range: {low} – {high}")
    if market_lines:
        risk_tags.append(RiskTag(name="Market Data", level="Info", note=" | ".join(market_lines)))
    buy_sell_note = _buy_sell_note(ctx)
    if buy_sell_note:
        pressure_level = "High" if ctx.buy_sell_ratio >= 0.65 or ctx.buy_sell_ratio <= 0.35 else "Medium"
        risk_tags.append(RiskTag(name="Buy/Sell Pressure", level=pressure_level, note=buy_sell_note))
    holder_quality_bits: list[str] = []
    if ctx.kol_holders > 0:
        bit = f"KOL {ctx.kol_holders}"
        if ctx.kol_holding_pct > 0:
            bit += f" ({ctx.kol_holding_pct:.1f}%)"
        holder_quality_bits.append(bit)
    if ctx.pro_holders > 0:
        bit = f"Pro {ctx.pro_holders}"
        if ctx.pro_holding_pct > 0:
            bit += f" ({ctx.pro_holding_pct:.1f}%)"
        holder_quality_bits.append(bit)
    if holder_quality_bits:
        risk_tags.append(RiskTag(name="Holder Quality", level="Info", note=" | ".join(holder_quality_bits)))
    momentum_note = _momentum_note(ctx)
    if momentum_note:
        positive_moves = sum(1 for value in (ctx.pct_change_5m, ctx.pct_change_1h, ctx.pct_change_4h) if value > 0)
        negative_moves = sum(1 for value in (ctx.pct_change_5m, ctx.pct_change_1h, ctx.pct_change_4h) if value < 0)
        momentum_level = "High" if positive_moves >= 2 else "Low" if negative_moves >= 2 else "Medium"
        risk_tags.append(RiskTag(name="Momentum", level=momentum_level, note=momentum_note))
    if ctx.futures_sentiment or ctx.futures_funding_rate != 0 or ctx.futures_long_short_ratio not in {0.0, 1.0}:
        futures_level = "High" if abs(ctx.futures_funding_rate) > 0.001 or ctx.futures_long_short_ratio > 2.5 or (0 < ctx.futures_long_short_ratio < 0.5) else "Medium"
        futures_note = []
        if ctx.futures_sentiment:
            futures_note.append(ctx.futures_sentiment.title())
        if ctx.futures_funding_rate != 0:
            futures_note.append(f"funding {ctx.futures_funding_rate * 100:+.4f}%")
        if ctx.futures_long_short_ratio > 0:
            futures_note.append(f"L/S {ctx.futures_long_short_ratio:.2f}")
        risk_tags.append(RiskTag(name="Futures Sentiment", level=futures_level, note=" | ".join(futures_note)))
    if ctx.is_meme_candidate and ctx.meme_lifecycle:
        risk_tags.append(RiskTag(name="Meme Lifecycle", level="Medium", note=f"{ctx.meme_lifecycle} | {ctx.meme_bonded_progress:.0f}% bonded"))
    if ctx.top_trader_interest:
        risk_tags.append(RiskTag(name="Top Trader Interest", level="Medium", note="Visible on top-earning trader tables"))

    # Enhanced: momentum score
    momentum = _compute_momentum_score(ctx)
    if momentum != 0:
        m_level = "High" if momentum > 3 else "Low" if momentum < -3 else "Medium"
        risk_tags.append(RiskTag(name="Momentum Score", level=m_level, note=f"{momentum:+.1f} (weighted multi-timeframe)"))

    # Enhanced: volume trend
    vol_trend = _volume_trend_note(ctx)
    if vol_trend:
        v_level = "High" if vol_trend == "spike" else "Medium" if vol_trend == "increasing" else "Low"
        risk_tags.append(RiskTag(name="Volume Trend", level=v_level, note=vol_trend.title()))

    # Enhanced: relative strength vs BTC
    rs_note = _relative_strength_note(ctx)
    if rs_note:
        relative = ctx.pct_change_24h - ctx.btc_change_24h
        rs_level = "High" if relative > 3 else "Low" if relative < -3 else "Medium"
        risk_tags.append(RiskTag(name="Relative Strength", level=rs_level, note=rs_note))

    # Enhanced: support/resistance levels
    if ctx.support_level > 0:
        risk_tags.append(RiskTag(name="Support", level="Info", note=f"${ctx.support_level:,.2f}"))
    if ctx.resistance_level > 0:
        risk_tags.append(RiskTag(name="Resistance", level="Info", note=f"${ctx.resistance_level:,.2f}"))

    if state == "blocked":
        quick_verdict = "Blocked. Audit risk is too high."
        quality = "Blocked"
        conviction = "Low"
    elif state == "thin":
        quick_verdict = "Thin read. No conviction yet."
        conviction = "Low"
    elif state == "unmatched":
        quick_verdict = "Monitor only. No signal match."
        conviction = "Low"
    elif state == "stale":
        quick_verdict = "Stale setup. Fresh confirmation needed."
        conviction = "Low"
    elif state == "late":
        quick_verdict = "Active but late. Exit pressure is rising."
        conviction = "Low"
    elif state == "active":
        if ctx.top_holder_concentration_pct >= CONCENTRATION_EXTREME:
            quick_verdict = "Active setup. Ownership risk is still heavy."
            conviction = "Medium"
        elif ctx.audit_gate == "WARN":
            quick_verdict = "Active setup. Audit caution still applies."
            conviction = "Medium"
        else:
            quick_verdict = "Active setup. Structure is supportive."
            conviction = "High"
    elif state == "early":
        quick_verdict = "Early setup. Structure is forming."
        conviction = "Medium" if evidence_level == "High" else "Low"
    else:
        quick_verdict = "Fragile setup. Confirmation still weak."

    top_risks = list(ctx.major_risks)
    if ctx.audit_gate == "BLOCK" and ctx.blocked_reason:
        top_risks.insert(0, ctx.blocked_reason)
    if not top_risks:
        if state == "thin":
            top_risks.append("Too much live token context is still missing, so this read should stay provisional.")
        if ctx.audit_flags:
            top_risks.append("Contract-level flags still weigh on the setup.")
        if state == "unmatched":
            top_risks.append("There is no matched live smart-money signal on the current board, so conviction should stay capped.")
        if ctx.exit_rate >= EXIT_RATE_HIGH:
            top_risks.append("Most tracked smart money may already be exiting, which makes the setup look late.")
        elif ctx.exit_rate >= EXIT_RATE_MODERATE:
            top_risks.append("Smart money exits are mixed already, so continuation quality may be less clean.")
        if ctx.signal_freshness == "STALE":
            top_risks.append("Signal timing is stale, so fresh confirmation matters more than the original trigger.")
        elif ctx.signal_freshness == "AGING":
            top_risks.append("Signal timing is aging and may degrade if new confirmation does not appear soon.")
        if ctx.top_holder_concentration_pct >= CONCENTRATION_EXTREME:
            top_risks.append("Top-holder concentration is very high, so ownership quality is less clean than headline strength suggests.")
        elif ctx.top_holder_concentration_pct >= CONCENTRATION_ELEVATED:
            top_risks.append("Ownership concentration is elevated, so conviction should stay selective.")
        if ctx.liquidity <= 0:
            top_risks.append("Liquidity context is missing or weak, which lowers confidence.")
        elif ctx.liquidity < LIQUIDITY_THIN:
            top_risks.append("Liquidity is very thin, so execution quality may be weaker than the setup suggests.")
        if not top_risks:
            top_risks.append("The setup still needs confirmation before attention turns into conviction.")

    return AnalysisBrief(
        entity=f"Token: {ctx.symbol}",
        quick_verdict=quick_verdict,
        signal_quality=quality,
        top_risks=top_risks,
        why_it_matters=_token_why_it_matters(ctx),
        what_to_watch_next=_token_watch_next(ctx),
        risk_tags=risk_tags,
        conviction=conviction,
        beginner_note="This is a research summary, not a buy/sell instruction.",
        audit_gate=ctx.audit_gate,
        blocked_reason=ctx.blocked_reason,
    )
