from __future__ import annotations

from src.formatters.heuristics import wallet_signal_quality
from src.models.context import WalletContext
from src.models.schemas import AnalysisBrief, RiskTag


def build_wallet_brief(ctx: WalletContext) -> AnalysisBrief:
    quality = wallet_signal_quality(ctx)
    conviction = "Medium" if quality == "Medium" and len(ctx.major_risks) <= 2 else "Low"

    risk_tags: list[RiskTag] = []
    if ctx.top_concentration_pct >= 70:
        risk_tags.append(RiskTag(name="Concentration Risk", level="High", note=f"Top concentration is {ctx.top_concentration_pct:.1f}%"))
    elif ctx.top_concentration_pct > 0:
        risk_tags.append(RiskTag(name="Concentration Risk", level="Medium", note=f"Top concentration is {ctx.top_concentration_pct:.1f}%"))

    if ctx.notable_exposures:
        risk_tags.append(RiskTag(name="Narrative Risk", level="Medium", note=", ".join(ctx.notable_exposures)))

    quick_verdict = "This wallet appears worth inspecting for behavior patterns, but concentration risk matters."
    if ctx.top_concentration_pct >= 70:
        quick_verdict = "This wallet looks highly concentrated, so behavior may be informative but risk is elevated."

    why_it_matters = (
        "Wallet analysis is useful when it explains behavior, not just balances. Concentration and exposure patterns matter more than raw size."
    )

    what_to_watch_next = [
        "rotation into new assets",
        "changes in top holding concentration",
        "whether the wallet enters trends early or late",
    ]

    return AnalysisBrief(
        entity=f"Wallet: {ctx.address}",
        quick_verdict=quick_verdict,
        signal_quality=quality,
        top_risks=ctx.major_risks or ["Wallet context is incomplete; treat this as lower-confidence."],
        why_it_matters=why_it_matters,
        what_to_watch_next=what_to_watch_next,
        risk_tags=risk_tags,
        conviction=conviction,
        beginner_note="Large wallet size alone does not guarantee smart-money quality.",
    )
