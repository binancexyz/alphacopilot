from __future__ import annotations

from src.analyzers.thresholds import RUGPULL_HIGH, RUGPULL_MODERATE
from src.models.schemas import AnalysisBrief, BriefSection, RiskTag
from src.analyzers.meme_analysis import analyze_meme
from src.services.factory import get_market_data_service
from src.services.snapshot_history import describe_snapshot_delta, save_snapshot
from src.utils.formatting import human_money as _human_money


_CONTRACT_KEYS = ("contract", "code", "verified", "mint", "owner", "blacklist", "proxy", "scam")
_LIQUIDITY_KEYS = ("liquidity", "tax", "sell", "buy", "slippage", "pool", "trade")
_STRUCTURE_KEYS = ("holder", "concentration", "risk level", "wash", "honeypot", "hidden", "risk")


def _pick_finding(items: list[str], *keywords: str) -> str:
    lower_keywords = [k.lower() for k in keywords]
    for item in items:
        lower = item.lower()
        if any(k in lower for k in lower_keywords):
            return item
    return ""



def _collect_matches(items: list[str], keywords: tuple[str, ...]) -> list[str]:
    matches: list[str] = []
    for item in items:
        lower = item.lower()
        if any(keyword in lower for keyword in keywords) and item not in matches:
            matches.append(item)
    return matches



def _rugpull_score(audit_gate: str, audit_flags: list[str], concentration: float, liquidity: float, buy_tax: float, sell_tax: float) -> tuple[int, str]:
    score = 0
    factors: list[str] = []

    if audit_gate == "BLOCK":
        score += 30
        factors.append("blocked audit")
    elif audit_gate == "WARN":
        score += 10
        factors.append("audit caution")

    # Contract flags
    dangerous_flags = {"scam", "honeypot", "blacklist", "hidden owner", "proxy", "not verified"}
    for flag in audit_flags:
        lower = flag.lower()
        if any(d in lower for d in dangerous_flags):
            score += 15
            factors.append(lower.split(",")[0].strip()[:30])
            break

    # Tax friction
    if sell_tax >= 10:
        score += 20
        factors.append(f"high sell tax {sell_tax:.0f}%")
    elif sell_tax >= 5:
        score += 10
        factors.append(f"elevated sell tax {sell_tax:.0f}%")

    # Concentration risk
    if concentration >= 80:
        score += 15
        factors.append("extreme concentration")
    elif concentration >= 50:
        score += 8
        factors.append("high concentration")

    # Liquidity
    if 0 < liquidity < 100_000:
        score += 10
        factors.append("very thin liquidity")
    elif 0 < liquidity < 500_000:
        score += 5
        factors.append("thin liquidity")

    score = min(score, 100)
    level = "High" if score >= RUGPULL_HIGH else "Moderate" if score >= RUGPULL_MODERATE else "Low"
    return score, f"{level} ({score}/100) — {', '.join(factors[:3])}" if factors else f"{level} ({score}/100)"


def _severity(audit_gate: str, risk_level: str, audit_limited: bool, audit_flags: list[str]) -> str:
    if audit_gate == "BLOCK":
        return "High"
    if audit_limited:
        return "Medium"
    if risk_level.lower() == "high":
        return "High"
    if risk_level.lower() == "low" and not audit_flags:
        return "Low"
    return "Medium"



def _verdict(audit_gate: str, risk_level: str, audit_limited: bool, audit_flags: list[str]) -> str:
    if audit_gate == "BLOCK":
        return "Avoid. Structural risk is too high."
    if audit_limited:
        return "Limited audit visibility. Stay cautious."
    if any("tax above 10%" in flag.lower() for flag in audit_flags):
        return "Tradable but flagged. Tax friction is high."
    if risk_level.lower() == "high":
        return "Structural caution. Risk flags are heavy."
    if audit_gate == "WARN" or audit_flags:
        return "Caution flags visible. Not clean yet."
    return "Clean audit. Normal caution still applies."



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
    signal_status = str(audit.get("signal_status") or "unknown").replace("|", "/")
    smart_money_count = int(audit.get("smart_money_count") or 0)
    signal_freshness = str(audit.get("signal_freshness") or "").replace("|", "/")
    price = float(audit.get("price") or 0)
    liquidity = float(audit.get("liquidity") or 0)
    volume_24h = float(audit.get("volume_24h") or 0)
    market_cap = float(audit.get("market_cap") or 0)
    buy_tax = float(audit.get("buy_tax") or 0)
    sell_tax = float(audit.get("sell_tax") or 0)
    combined = [x for x in [blocked_reason, *audit_flags, *risks] if x]
    audit_valid = bool(audit.get("has_result", audit.get("hasResult", False))) and bool(audit.get("is_supported", audit.get("isSupported", False)))
    audit_limited = not audit_valid or "limited" in audit_summary.lower() or "partial" in blocked_reason.lower() or "unavailable" in blocked_reason.lower()

    verdict = _verdict(audit_gate, risk_level, audit_limited, audit_flags)
    if audit_gate == "BLOCK" and smart_money_count > 0 and signal_status in {"watch", "bullish", "triggered", "active"}:
        verdict = f"{verdict} Smart money is still active, but the audit risk still overrides that interest."
    severity = _severity(audit_gate, risk_level, audit_limited, audit_flags)

    contract_matches = _collect_matches(combined, _CONTRACT_KEYS)
    liquidity_matches = _collect_matches(combined, _LIQUIDITY_KEYS)
    structure_matches = _collect_matches(combined, _STRUCTURE_KEYS)

    contract_hit = blocked_reason if audit_gate == "BLOCK" else (contract_matches[0] if contract_matches else "")
    liquidity_hit = liquidity_matches[0] if liquidity_matches else ""
    structure_hit = structure_matches[0] if structure_matches else ""

    if contract_hit:
        primary = f"Contract: {contract_hit}"
    elif audit_limited:
        primary = "Contract: Partial visibility ⚠️"
    else:
        primary = "Contract: No red flags"

    liquidity_line = ""
    if liquidity_hit:
        liquidity_line = f"Liquidity: {liquidity_hit}"
    elif liquidity > 0:
        liquidity_line = f"Liquidity: {_human_money(liquidity)} visible"
    elif audit_limited:
        liquidity_line = "Liquidity: Partial visibility ⚠️"
    elif any("tax" in flag.lower() for flag in audit_flags):
        liquidity_line = f"Liquidity: {next(flag for flag in audit_flags if 'tax' in flag.lower())}"
    else:
        liquidity_line = "Liquidity: Adequate"

    if structure_hit:
        structure_line = f"Structure: {structure_hit}"
    elif audit_gate == "BLOCK":
        structure_line = "Structure: Weak"
    elif audit_limited:
        structure_line = "Structure: Partial"
    elif risk_level.lower() == "low":
        structure_line = "Structure: Stable"
    else:
        structure_line = f"Structure: {risk_level} risk"

    findings = [primary]
    if buy_tax > 0 or sell_tax > 0:
        findings.append(f"Tax: Buy {buy_tax:.2f}% / Sell {sell_tax:.2f}%")
    if liquidity_line and liquidity_line not in findings and len(findings) < 3:
        findings.append(liquidity_line)
    if structure_line and structure_line not in findings and len(findings) < 3:
        findings.append(structure_line)
    while len(findings) < 3:
        findings.append("")

    packed = "|".join([
        display_name,
        display_symbol,
        severity,
        audit_summary,
        findings[0],
        findings[1],
        findings[2],
        audit_gate.lower(),
        verdict,
    ])

    tags: list[RiskTag] = []
    if audit_limited:
        tags.append(RiskTag(name="Audit Validity", level="Limited", note="Live audit validity is partial or unsupported right now."))
    elif audit_valid:
        tags.append(RiskTag(name="Audit Validity", level="Valid", note="Result is based on a supported audit payload."))
    tags.append(RiskTag(name="Severity", level=severity, note=risk_level))

    # Rug-pull probability score
    concentration = float(audit.get("top_holder_concentration_pct") or 0)
    rugpull_score, rugpull_note = _rugpull_score(audit_gate, audit_flags, concentration, liquidity, buy_tax, sell_tax)
    rugpull_level = "High" if rugpull_score >= RUGPULL_HIGH else "Medium" if rugpull_score >= RUGPULL_MODERATE else "Low"
    tags.append(RiskTag(name="Rug-Pull Risk", level=rugpull_level, note=rugpull_note))

    sections: list[BriefSection] = []
    if smart_money_count > 0 or signal_status not in {"", "unknown", "unmatched"}:
        signal_lines = [f"Setup: {signal_status or 'unknown'}"]
        if smart_money_count > 0:
            signal_lines.append(f"Participation: {smart_money_count} smart-money wallet(s)")
        if signal_freshness and signal_freshness != "UNKNOWN":
            signal_lines.append(f"Timing: {signal_freshness.title()}")
        if audit_gate == "BLOCK" and smart_money_count > 0:
            signal_lines.append("Despite the audit risk, tracked smart money is still participating.")
        sections.append(BriefSection(title="📡 Signal Lens", content="\n".join(f"- {line}" for line in signal_lines if line)))
    market_lines: list[str] = []
    if price > 0:
        market_lines.append(f"Price: ${price:,.2f}")
    if volume_24h > 0:
        market_lines.append(f"Volume 24h: {_human_money(volume_24h)}")
    if market_cap > 0:
        market_lines.append(f"Market Cap: {_human_money(market_cap)}")
    if market_lines:
        sections.append(BriefSection(title="📊 Market Context", content="\n".join(f"- {line}" for line in market_lines)))
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
                if tag.name == "Bonding Progress":
                    meme_tags.append(f"{tag.name}: {tag.note}")
                if tag.name == "DEX Migration":
                    meme_tags.append(f"{tag.name}: {tag.note}")
            meme_lines = meme_tags[:4]
            if meme_lines:
                sections.append(BriefSection(title="🧪 Meme Lens", content="\n".join(f"- {line}" for line in meme_lines if line)))
    except Exception:
        tags.append(RiskTag(name="Meme Lens", level="Info", note="Meme lens unavailable"))

    brief = AnalysisBrief(
        entity=f"Audit: {display_symbol}",
        quick_verdict=packed,
        signal_quality=severity,
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

    # Historical audit trail
    snapshot_data = {
        "audit_gate": audit_gate,
        "severity": severity,
        "rugpull_score": rugpull_score,
        "flags_count": len(audit_flags),
    }
    try:
        from src.services.snapshot_history import latest_snapshot as _latest
        prev = _latest("audit", display_symbol)
        if prev:
            prev_gate = str(prev.get("audit_gate") or "")
            if prev_gate and prev_gate != audit_gate:
                trail_note = f"Gate changed: {prev_gate} → {audit_gate}"
                brief.risk_tags.append(RiskTag(name="Audit Trail", level="Medium", note=trail_note))
            elif prev_gate == audit_gate:
                brief.risk_tags.append(RiskTag(name="Audit Trail", level="Info", note="No change since last check"))
        else:
            brief.risk_tags.append(RiskTag(name="Audit Trail", level="Info", note="First audit check recorded"))
        save_snapshot("audit", display_symbol, snapshot_data)
    except Exception:
        pass

    return brief
