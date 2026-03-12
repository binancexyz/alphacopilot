from __future__ import annotations

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
    if ctx.signal_freshness != "UNKNOWN":
        pieces.append(f"Signal timing reads as {ctx.signal_freshness.lower()} ({ctx.signal_age_hours:.1f}h old).")
    if not pieces:
        pieces.append(_token_price_line(ctx))
    return " ".join(pieces[:3]).strip()


def _token_watch_next(ctx: TokenContext) -> list[str]:
    watch: list[str] = []
    if ctx.audit_gate == "BLOCK":
        watch.append("do not treat the signal as actionable unless the audit picture changes materially")
        return watch

    if ctx.signal_status in {"watch", "bullish", "triggered"}:
        watch.append("whether the current signal status improves from attention into real follow-through")
    else:
        watch.append("whether a clearer signal status appears instead of vague market attention")

    if ctx.exit_rate >= 70:
        watch.append("whether smart-money exit pressure cools down, because the current setup already looks late")
    elif ctx.exit_rate >= 40:
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


def build_token_brief(ctx: TokenContext) -> AnalysisBrief:
    quality = token_signal_quality(ctx)
    conviction = token_conviction(ctx)
    evidence_level, evidence_note = _token_evidence_level(ctx)

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

    if ctx.audit_gate == "BLOCK":
        quick_verdict = "Blocked. Audit risk too high."
        quality = "Blocked"
        conviction = "Low"
    elif evidence_level == "Low":
        quick_verdict = "Thin read. No conviction yet."
        conviction = "Low"
    elif ctx.signal_status == "unmatched":
        quick_verdict = "Monitor only. No signal match."
    elif quality == "High" and conviction == "High":
        quick_verdict = "Strong setup. Risk still matters."
    elif quality == "High":
        quick_verdict = "Serious setup. Needs cleaner follow-through."
    elif quality == "Medium":
        quick_verdict = "Watch closely. Still conditional."
    else:
        quick_verdict = "Thin structure. Confirmation needed."

    top_risks = list(ctx.major_risks)
    if ctx.audit_gate == "BLOCK" and ctx.blocked_reason:
        top_risks.insert(0, ctx.blocked_reason)
    if not top_risks:
        if evidence_level == "Low":
            top_risks.append("Too much live token context is still missing, so this read should stay provisional.")
        if ctx.audit_flags:
            top_risks.append("Contract-level flags still weigh on the setup.")
        if ctx.signal_status == "unmatched":
            top_risks.append("There is no matched live smart-money signal on the current board, so conviction should stay capped.")
        if ctx.exit_rate >= 70:
            top_risks.append("Most tracked smart money may already be exiting, which makes the setup look late.")
        elif ctx.exit_rate >= 40:
            top_risks.append("Smart money exits are mixed already, so continuation quality may be less clean.")
        if ctx.signal_freshness == "STALE":
            top_risks.append("Signal timing is stale, so fresh confirmation matters more than the original trigger.")
        elif ctx.signal_freshness == "AGING":
            top_risks.append("Signal timing is aging and may degrade if new confirmation does not appear soon.")
        if ctx.liquidity <= 0:
            top_risks.append("Liquidity context is missing or weak, which lowers confidence.")
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
