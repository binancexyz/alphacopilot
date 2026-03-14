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
    if ctx.is_meme_candidate and ctx.meme_lifecycle:
        pieces.append(f"Meme lifecycle reads {ctx.meme_lifecycle} with bonding progress near {ctx.meme_bonded_progress:.0f}%.")
    if ctx.top_trader_interest:
        pieces.append("Top-trader PnL tables also show this symbol among recent top earners.")
    if not pieces:
        pieces.append(_token_price_line(ctx))
    return " ".join(pieces[:3]).strip()


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
