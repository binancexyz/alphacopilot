from __future__ import annotations

from src.models.schemas import AnalysisBrief, BriefSection, RiskTag
from src.analyzers.meme_analysis import analyze_meme
from src.services.factory import get_market_data_service


def _pick_finding(items: list[str], *keywords: str) -> str:
    lower_keywords = [k.lower() for k in keywords]
    for item in items:
        lower = item.lower()
        if any(k in lower for k in lower_keywords):
            return item
    return ""


def analyze_audit(symbol: str) -> AnalysisBrief:
    service = get_market_data_service()
    audit = service.get_audit_context(symbol)

    display_symbol = str(audit.get("symbol") or symbol).replace("|", "/")
    display_name = str(audit.get("display_name") or display_symbol).replace("|", "/")
    audit_gate = str(audit.get("audit_gate") or "WARN").replace("|", "/")
    blocked_reason = str(audit.get("blocked_reason") or "").replace("|", "/")
    risk_level = str(audit.get("risk_level") or ("High" if audit_gate == "BLOCK" else "Medium" if audit_gate == "WARN" else "Low")).replace("|", "/")
    audit_summary = str(audit.get("audit_summary") or blocked_reason or "Audit output is limited right now.").replace("|", " / ")
    audit_flags = [str(x).replace("|", " / ") for x in audit.get("audit_flags", [])]
    risks = [str(x).replace("|", " / ") for x in audit.get("major_risks", [])]
    audit_valid = bool(audit.get("has_result", audit.get("hasResult", False))) and bool(audit.get("is_supported", audit.get("isSupported", False)))
    audit_limited = not audit_valid or "limited" in audit_summary.lower() or "partial" in blocked_reason.lower() or "unavailable" in blocked_reason.lower()

    if audit_gate == "BLOCK":
        verdict = "Avoid until live context improves."
    elif audit_limited:
        verdict = "Partial read. Stay cautious."
    elif audit_gate == "WARN":
        verdict = "Caution flags visible. Not clean yet."
    else:
        verdict = "Clean audit. Normal caution still applies."

    contract_hit = blocked_reason or _pick_finding(audit_flags + risks, "contract", "code", "verified", "mint", "owner", "blacklist", "proxy")
    liquidity_hit = _pick_finding(audit_flags + risks, "liquidity", "tax", "sell", "buy", "slippage", "pool")
    structure_hit = _pick_finding(audit_flags + risks, "holder", "concentration", "risk level", "wash", "honeypot", "hidden")

    if contract_hit:
        primary = f"Contract: {contract_hit}"
    else:
        primary = "Contract: No red flags"

    if liquidity_hit:
        secondary = f"Liquidity: {liquidity_hit}"
    elif audit_limited:
        secondary = "Liquidity: Partial visibility ⚠️"
    else:
        secondary = "Liquidity: Adequate"

    if structure_hit:
        tertiary = f"Structure: {structure_hit}"
    elif audit_gate == "BLOCK":
        tertiary = "Structure: Weak"
    elif risk_level.lower() == "low":
        tertiary = "Structure: Stable"
    elif audit_limited:
        tertiary = "Structure: Partial"
    else:
        tertiary = f"Structure: {risk_level} risk"

    packed = "|".join([
        display_name,
        display_symbol,
        risk_level,
        audit_summary,
        primary,
        secondary,
        tertiary,
        audit_gate.lower(),
        verdict,
    ])

    tags: list[RiskTag] = []
    if audit_limited:
        tags.append(RiskTag(name="Audit Validity", level="Limited", note="Live audit validity is partial or unsupported right now."))
    elif audit_valid:
        tags.append(RiskTag(name="Audit Validity", level="Valid", note="Result is based on a supported audit payload."))

    sections: list[BriefSection] = []
    try:
        meme_brief = analyze_meme(symbol)
        meme_note = meme_brief.quick_verdict.strip()
        lower_note = meme_note.lower()
        show_meme = not any([
            "does not currently read as a strong meme candidate" in lower_note,
            "not a strong meme candidate" in lower_note,
        ])
        if show_meme:
            participation_tag = next((tag for tag in meme_brief.risk_tags if tag.name == "Participation Quality"), None)
            lifecycle_tag = next((tag for tag in meme_brief.risk_tags if tag.name == "Lifecycle"), None)
            if participation_tag and lifecycle_tag:
                show_meme = not (participation_tag.level == "Low" and str(lifecycle_tag.note or lifecycle_tag.level).lower() in {"unknown", "inactive"})
        if show_meme:
            meme_tags = []
            for tag in meme_brief.risk_tags:
                if tag.name in {"Participation Quality", "Lifecycle"}:
                    suffix = f": {tag.note}" if tag.note else ""
                    meme_tags.append(f"{tag.name}: {tag.level}{suffix}")
            meme_lines = meme_tags[:2]
            if meme_lines:
                sections.append(BriefSection(title="🧪 Meme Lens", content="\n".join(f"- {line}" for line in meme_lines if line)))
    except Exception:
        pass

    return AnalysisBrief(
        entity=f"Audit: {display_symbol}",
        quick_verdict=packed,
        signal_quality=risk_level,
        top_risks=[],
        why_it_matters="",
        what_to_watch_next=[],
        risk_tags=tags,
        sections=sections,
        conviction=None,
        beginner_note=None,
        audit_gate=audit_gate,
        blocked_reason=blocked_reason,
    )
