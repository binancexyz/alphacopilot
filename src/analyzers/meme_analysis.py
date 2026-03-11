from __future__ import annotations

from src.models.schemas import AnalysisBrief, RiskTag
from src.services.factory import get_market_data_service
from src.services.normalizers import normalize_meme_context


def analyze_meme(symbol: str) -> AnalysisBrief:
    service = get_market_data_service()
    ctx = normalize_meme_context(service.get_meme_context(symbol))

    tags: list[RiskTag] = []
    tags.append(RiskTag(name="Lifecycle", level="Medium", note=ctx.lifecycle_stage))
    if ctx.launch_platform:
        tags.append(RiskTag(name="Launch Platform", level="Low", note=ctx.launch_platform))
    if ctx.is_alpha:
        tags.append(RiskTag(name="Alpha", level="Medium", note="Marked alpha in current signal context."))
    if ctx.signal_freshness != "UNKNOWN":
        tags.append(RiskTag(name="Timing", level="High" if ctx.signal_freshness == "STALE" else "Medium" if ctx.signal_freshness == "AGING" else "Low", note=f"{ctx.signal_freshness.title()} | {ctx.signal_age_hours:.1f}h old"))

    if ctx.audit_gate == "BLOCK":
        verdict = f"{ctx.display_name} is blocked as a meme setup because the audit layer is too dangerous to ignore."
        quality = "Blocked"
        conviction = "Low"
    elif ctx.lifecycle_stage == "active" and ctx.smart_money_count > 0 and ctx.signal_freshness == "FRESH":
        verdict = f"{ctx.display_name} has a live meme-style setup with visible smart-money activity, but it still needs fast discipline because meme timing degrades quickly."
        quality = "Medium"
        conviction = "Medium"
    elif ctx.lifecycle_stage in {"attention", "active"}:
        verdict = f"{ctx.display_name} has meme-style attention, but the current setup still looks too conditional to trust aggressively."
        quality = "Low"
        conviction = "Low"
    else:
        verdict = f"{ctx.display_name} does not currently read as a strong meme candidate from the available live context."
        quality = "Low"
        conviction = "Low"

    why_bits = []
    if ctx.launch_platform:
        why_bits.append(f"Launch platform: {ctx.launch_platform}.")
    why_bits.append(f"Lifecycle: {ctx.lifecycle_stage}.")
    if ctx.market_rank_context:
        why_bits.append(ctx.market_rank_context)
    if ctx.smart_money_count > 0:
        why_bits.append(f"{ctx.smart_money_count} smart-money wallets are visible.")
    if ctx.signal_freshness != "UNKNOWN":
        why_bits.append(f"Timing is {ctx.signal_freshness.lower()} ({ctx.signal_age_hours:.1f}h old).")
    why = " ".join(why_bits).strip()

    risks = list(ctx.major_risks)
    if ctx.audit_gate == "BLOCK" and ctx.blocked_reason:
        risks.insert(0, ctx.blocked_reason)
    if not risks:
        if ctx.exit_rate >= 70:
            risks.append("Most tracked smart money may already be exiting, which makes this meme setup look late.")
        elif ctx.exit_rate >= 40:
            risks.append("Exit rate is already mixed, so continuation quality may be weaker than the hype suggests.")
        elif ctx.lifecycle_stage not in {"attention", "active", "finalizing"}:
            risks.append("Current live context is too weak to treat this as a strong meme candidate.")
        else:
            risks.append("Meme attention can reverse quickly even when early interest looks strong.")

    watch = []
    if ctx.audit_gate == "BLOCK":
        watch.append("do not treat the meme setup as actionable unless the audit picture changes")
    else:
        if ctx.bonded_progress >= 90:
            watch.append(f"whether bonding progress completes cleanly from {ctx.bonded_progress:.0f}% instead of turning chaotic")
        elif ctx.bonded_progress > 0:
            watch.append(f"whether bonding progress builds from {ctx.bonded_progress:.0f}% into a cleaner launch state")
        elif ctx.lifecycle_stage == "attention":
            watch.append("whether attention develops into a cleaner active meme setup instead of fading as a loose narrative")
        if ctx.exit_rate >= 70:
            watch.append("whether exit pressure cools down, because the current setup already looks late")
        else:
            watch.append("whether smart-money interest expands instead of fading after the first burst")

    return AnalysisBrief(
        entity=f"Meme: {ctx.symbol}",
        quick_verdict=verdict,
        signal_quality=quality,
        top_risks=risks,
        why_it_matters=why,
        what_to_watch_next=watch,
        risk_tags=tags,
        conviction=conviction,
        audit_gate=ctx.audit_gate,
        blocked_reason=ctx.blocked_reason,
    )
