from __future__ import annotations

from src.analyzers.thresholds import (
    CONCENTRATION_ELEVATED,
    CONCENTRATION_EXTREME,
    CONCENTRATION_HIGH,
    CONCENTRATION_MEANINGFUL,
)
from src.formatters.heuristics import wallet_signal_quality
from src.models.context import WalletContext
from src.models.schemas import AnalysisBrief, RiskTag


def _wallet_evidence_level(ctx: WalletContext) -> tuple[str, str]:
    score = 0
    if ctx.portfolio_value > 0:
        score += 1
    if ctx.holdings_count > 0:
        score += 1
    if ctx.top_holdings:
        score += 1
    if ctx.notable_exposures:
        score += 1
    if ctx.style_read:
        score += 1
    if ctx.change_24h != 0:
        score += 1

    if score >= 5:
        return "High", "The wallet has enough live structure to support a more useful behavior read."
    if score >= 3:
        return "Medium", "The wallet read is usable, but some exposure or behavior context is still thin."
    return "Low", "The wallet read is provisional because the current live evidence is too thin for a strong follow judgment."


def _format_holding_summary(ctx: WalletContext) -> str:
    if not ctx.top_holdings:
        return "Top holding detail is limited, so this wallet still needs more behavior context before strong conclusions."

    top_bits = [f"{holding.symbol} ({holding.weight_pct:.1f}%)" for holding in ctx.top_holdings[:3]]
    return f"Top visible holdings are {', '.join(top_bits)}, which gives a better clue about style and concentration than wallet size alone."


def _concentration_read(ctx: WalletContext) -> str:
    if ctx.top_concentration_pct >= CONCENTRATION_EXTREME:
        return "extreme concentration"
    if ctx.top_concentration_pct >= CONCENTRATION_HIGH:
        return "high concentration"
    if ctx.top_concentration_pct >= CONCENTRATION_MEANINGFUL:
        return "meaningful concentration"
    if ctx.top_concentration_pct > 0:
        return "controlled concentration"
    return "unknown concentration"


def _activity_read(ctx: WalletContext) -> str:
    if ctx.change_24h >= 10:
        return f"very active 24h change at {ctx.change_24h:+.1f}%"
    if ctx.change_24h >= 3:
        return f"positive 24h change at {ctx.change_24h:+.1f}%"
    if ctx.change_24h <= -10:
        return f"sharp 24h drawdown at {ctx.change_24h:+.1f}%"
    if ctx.change_24h <= -3:
        return f"negative 24h change at {ctx.change_24h:+.1f}%"
    if ctx.change_24h != 0:
        return f"muted 24h change at {ctx.change_24h:+.1f}%"
    return "little visible 24h movement"


def _wallet_style_profile(ctx: WalletContext) -> str:
    if ctx.style_profile:
        return ctx.style_profile
    if ctx.top_concentration_pct >= 75:
        return "Concentrated Conviction"
    if ctx.top_concentration_pct >= 50:
        return "Focused Rotation"
    if ctx.holdings_count >= 10 and ctx.top_concentration_pct <= 35:
        return "Broad Basket"
    if ctx.notable_exposures:
        return "Narrative Tilt"
    return "Mixed Observer"


def _wallet_why_it_matters(ctx: WalletContext) -> str:
    pieces: list[str] = []
    if ctx.portfolio_value > 0:
        pieces.append(f"This wallet tracks roughly ${ctx.portfolio_value:,.0f} across {ctx.holdings_count} holding(s), so it is large enough to inspect for behavior rather than treating it as random dust.")
    elif ctx.holdings_count > 0:
        pieces.append(f"This wallet shows {ctx.holdings_count} holding(s), which is enough to inspect for concentration and rotation patterns.")

    pieces.append(f"Current read: {_concentration_read(ctx)} with {_activity_read(ctx)}.")
    pieces.append(f"Behavior profile: {_wallet_style_profile(ctx)}.")

    if ctx.style_read:
        pieces.append(ctx.style_read)
    else:
        pieces.append(_format_holding_summary(ctx))
    if ctx.exposure_breakdown:
        pieces.append(f"Exposure mix: {', '.join(ctx.exposure_breakdown[:3])}.")
    return " ".join(pieces[:4]).strip()


def _wallet_watch_next(ctx: WalletContext) -> list[str]:
    watch: list[str] = []
    if ctx.change_24h > 0:
        watch.append("whether recent gains are being held, expanded, or rotated out of")
    elif ctx.change_24h < 0:
        watch.append("whether recent drawdown leads to rotation, defense, or fresh accumulation")
    else:
        watch.append("whether the wallet starts rotating into new assets or stays static")

    if ctx.top_concentration_pct >= 70:
        watch.append("whether concentration keeps increasing or begins to spread across more holdings")
    else:
        watch.append("whether top holding concentration stays controlled as new positions appear")

    if ctx.notable_exposures:
        watch.append(f"whether exposure to {', '.join(ctx.notable_exposures[:2])} proves early, crowded, or late")
    else:
        watch.append("whether the wallet starts clustering around a clearer narrative")
    return watch


def build_wallet_brief(ctx: WalletContext) -> AnalysisBrief:
    quality = wallet_signal_quality(ctx)
    conviction = "Medium" if quality == "Medium" and len(ctx.major_risks) <= 2 else "Low"
    evidence_level, evidence_note = _wallet_evidence_level(ctx)

    risk_tags: list[RiskTag] = [RiskTag(name="Evidence Quality", level=evidence_level, note=evidence_note)]
    if ctx.top_concentration_pct >= 70:
        risk_tags.append(RiskTag(name="Concentration Risk", level="High", note=f"Top concentration is {ctx.top_concentration_pct:.1f}%"))
    elif ctx.top_concentration_pct > 0:
        risk_tags.append(RiskTag(name="Concentration Risk", level="Medium", note=f"Top concentration is {ctx.top_concentration_pct:.1f}%"))

    if ctx.change_24h != 0:
        activity_level = "High" if abs(ctx.change_24h) >= 10 else "Medium" if abs(ctx.change_24h) >= 3 else "Low"
        risk_tags.append(RiskTag(name="Activity", level=activity_level, note=f"24h change {ctx.change_24h:+.1f}%"))

    if ctx.notable_exposures:
        risk_tags.append(RiskTag(name="Narrative Risk", level="Medium", note=", ".join(ctx.notable_exposures[:3])))
    risk_tags.append(RiskTag(name="Style Profile", level="Low", note=_wallet_style_profile(ctx)))

    thin_context = ctx.portfolio_value <= 0 and ctx.holdings_count <= 0 and not ctx.top_holdings
    partial_context = not thin_context and evidence_level == "Low"

    if thin_context:
        quick_verdict = "Too thin to read. Return after rotation activity."
        ctx.follow_verdict = "Unknown"
        conviction = "Low"
    elif partial_context:
        quick_verdict = "Limited read. Some structure visible."
        ctx.follow_verdict = "Unknown"
        conviction = "Low"
    elif ctx.follow_verdict == "Track" and ctx.top_concentration_pct < CONCENTRATION_ELEVATED:
        quick_verdict = "Trackable wallet. Useful behavior signal."
        conviction = "Medium"
    elif ctx.follow_verdict == "Track":
        quick_verdict = "Trackable wallet. Concentration still high."
    elif ctx.follow_verdict == "Don't follow":
        quick_verdict = "Not enough structure. Do not follow."
    elif ctx.top_concentration_pct >= 75:
        quick_verdict = "Readable wallet. Concentration too high to trust."
    elif ctx.top_concentration_pct >= 50:
        quick_verdict = "Monitor only. Concentration still high."
    elif quality == "Medium":
        quick_verdict = "Readable wallet. Pattern signal exists."
    else:
        quick_verdict = "Some structure visible. Needs more history."

    risk_tags.append(RiskTag(name="Follow Verdict", level="Low" if ctx.follow_verdict == "Track" else "Medium" if ctx.follow_verdict == "Unknown" else "High", note=ctx.follow_verdict))

    top_risks = list(ctx.major_risks)
    if not top_risks:
        if thin_context:
            top_risks.append("Current live wallet context is too thin to support a strong behavior judgment.")
        if ctx.top_concentration_pct >= 75:
            top_risks.append("Extreme concentration means one position can dominate the whole read.")
        elif ctx.top_concentration_pct >= 60:
            top_risks.append("High concentration can turn one bad position into a large portfolio hit.")
        if abs(ctx.change_24h) >= 10:
            top_risks.append("Large 24h movement can make one snapshot look smarter or worse than the underlying behavior really is.")
        if not ctx.top_holdings:
            top_risks.append("Top holding detail is too thin to judge intent confidently.")
        if not top_risks:
            top_risks.append("Wallet behavior needs repeated observation before it deserves strong smart-money claims.")

    return AnalysisBrief(
        entity=f"Wallet: {ctx.address}",
        quick_verdict=quick_verdict,
        signal_quality=quality,
        top_risks=top_risks,
        why_it_matters=_wallet_why_it_matters(ctx) if not thin_context else "Current live wallet evidence is limited, so this read should be treated as provisional rather than definitive.",
        what_to_watch_next=_wallet_watch_next(ctx),
        risk_tags=risk_tags,
        conviction=conviction,
        beginner_note="A big wallet is not automatically a smart wallet. The useful signal is in behavior, concentration, and timing.",
    )
