from __future__ import annotations

from src.models.schemas import AnalysisBrief
from src.services.factory import get_market_data_service


def analyze_audit(symbol: str) -> AnalysisBrief:
    service = get_market_data_service()
    audit = service.get_audit_context(symbol)

    display_symbol = str(audit.get("symbol") or symbol)
    display_name = str(audit.get("display_name") or display_symbol)
    audit_gate = str(audit.get("audit_gate") or "WARN")
    blocked_reason = str(audit.get("blocked_reason") or "")
    risk_level = str(audit.get("risk_level") or ("High" if audit_gate == "BLOCK" else "Medium" if audit_gate == "WARN" else "Low"))
    audit_summary = str(audit.get("audit_summary") or blocked_reason or "Audit output is limited right now.")
    audit_flags = [str(x) for x in audit.get("audit_flags", [])]
    risks = [str(x) for x in audit.get("major_risks", [])]

    if audit_gate == "BLOCK":
        verdict = f"{display_name} fails the current audit gate, so it should be treated as blocked until the security picture changes."
    elif audit_gate == "WARN":
        verdict = f"{display_name} has a usable audit read, but caution flags mean it should not be treated as clean."
    else:
        verdict = f"{display_name} passes the current audit gate more cleanly than most risky edge cases, but it still deserves normal caution."

    primary = blocked_reason or (audit_flags[0] if audit_flags else (risks[0] if risks else "No major security issue surfaced in the current audit payload."))
    secondary = audit_flags[1] if len(audit_flags) > 1 else (risks[1] if len(risks) > 1 else "")

    packed = "|".join([
        display_name,
        display_symbol,
        risk_level,
        audit_summary,
        primary,
        secondary,
        "0",
        audit_gate.lower(),
        verdict,
    ])

    return AnalysisBrief(
        entity=f"Audit: {display_symbol}",
        quick_verdict=packed,
        signal_quality=risk_level,
        top_risks=[],
        why_it_matters="",
        what_to_watch_next=[],
        risk_tags=[],
        conviction=None,
        beginner_note=None,
        audit_gate=audit_gate,
        blocked_reason=blocked_reason,
    )
