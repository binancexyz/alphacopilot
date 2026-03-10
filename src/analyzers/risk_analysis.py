from __future__ import annotations

from src.services.factory import get_market_data_service
from src.services.normalizers import normalize_signal_context, normalize_token_context
from src.models.schemas import AnalysisBrief


def analyze_risk(symbol: str) -> AnalysisBrief:
    service = get_market_data_service()
    token_raw = service.get_token_context(symbol)
    signal_raw = service.get_signal_context(symbol)

    token = normalize_token_context(token_raw)
    signal = normalize_signal_context(signal_raw)

    audit_summary = "; ".join(token.audit_flags[:2]) if token.audit_flags else "No obvious contract red flags surfaced in the current brief."
    top_risk = token.major_risks[0] if token.major_risks else signal.major_risks[0] if signal.major_risks else "Risk context is still incomplete, so caution should stay elevated."
    second_risk = token.major_risks[1] if len(token.major_risks) > 1 else signal.major_risks[1] if len(signal.major_risks) > 1 else ""

    if token.audit_flags:
        risk_level = "High"
        verdict = "The biggest caution is structural: contract-level transparency or safety checks are not fully clean yet."
    elif token.liquidity <= 0:
        risk_level = "High"
        verdict = "The biggest caution is weak market structure because liquidity context is too thin."
    elif signal.signal_status not in {"triggered", "bullish"}:
        risk_level = "Medium"
        verdict = "The setup is not broken, but the risk is that attention never turns into durable confirmation."
    else:
        risk_level = "Medium"
        verdict = "Risk is present but looks more manageable than catastrophic right now."

    packed = "|".join([
        token.display_name,
        token.symbol,
        risk_level,
        audit_summary,
        top_risk,
        second_risk,
        str(token.liquidity),
        signal.signal_status,
        verdict,
    ])

    return AnalysisBrief(
        entity=f"Risk: {token.symbol}",
        quick_verdict=packed,
        signal_quality=risk_level,
        top_risks=[],
        why_it_matters="",
        what_to_watch_next=[],
        risk_tags=[],
        conviction=None,
        beginner_note=None,
    )
