from __future__ import annotations

from src.formatters.conviction import conviction_label
from src.models.schemas import AnalysisBrief, RiskTag
from src.services.factory import get_market_data_service


def analyze_wallet(address: str) -> AnalysisBrief:
    service = get_market_data_service()
    context = service.get_wallet_context(address)
    risk_tags = [
        RiskTag(name="Concentration Risk", level="High", note="Wallet may depend heavily on a few positions."),
        RiskTag(name="Narrative Risk", level="Medium", note="Performance may be tied to short-lived themes."),
    ]
    brief = AnalysisBrief(
        entity=f"Wallet: {address}",
        quick_verdict=context.get("quick_context", "This wallet appears worth inspecting for behavior patterns, but concentration risk matters."),
        signal_quality=f"{context.get('signal_quality', 'Medium')} — potentially informative wallet behavior, but quality depends on consistency and context.",
        top_risks=context.get("risks", []),
        why_it_matters="Wallet analysis is useful when it explains behavior, not just balances. Concentration and rotation patterns matter more than raw size.",
        what_to_watch_next=[
            "rotation into new assets",
            "changes in top holding concentration",
            "whether the wallet enters trends early or late",
        ],
        risk_tags=risk_tags,
    )
    brief.conviction = conviction_label(brief.signal_quality, len(brief.top_risks))
    return brief
