from __future__ import annotations

from src.models.schemas import AnalysisBrief


ENTITY_EMOJI = {
    "Token:": "🪙",
    "Brief:": "🧩",
    "Price:": "💵",
    "Risk:": "🛡️",
    "Audit:": "🔐",
    "Signal:": "📡",
    "Wallet:": "👛",
    "Market Watch": "🌐",
}


def _entity_line(entity: str) -> str:
    for prefix, emoji in ENTITY_EMOJI.items():
        if entity.startswith(prefix) or entity == prefix:
            return f"**{emoji} {entity}**"
    return f"**📌 {entity}**"


def _human_money(value: float) -> str:
    abs_value = abs(value)
    if abs_value >= 1_000_000_000_000:
        return f"${value/1_000_000_000_000:.1f}T"
    if abs_value >= 1_000_000_000:
        return f"${value/1_000_000_000:.1f}B"
    if abs_value >= 1_000_000:
        return f"${value/1_000_000:.1f}M"
    if abs_value >= 1_000:
        return f"${value/1_000:.1f}K"
    return f"${value:,.2f}"


def _format_price_card(brief: AnalysisBrief) -> str:
    name, symbol, link, rank = (brief.quick_verdict.split("|", 3) + ["", "", "", "0"])[:4]
    price, change_24h, high_24h, low_24h, market_cap, volume_24h, arrow = (brief.why_it_matters.split("|", 6) + ["0", "0", "0", "0", "0", "0", "➖"])[:7]

    try:
        price_f = float(price or 0)
        change_f = float(change_24h or 0)
        high_f = float(high_24h or 0)
        low_f = float(low_24h or 0)
        market_cap_f = float(market_cap or 0)
        volume_f = float(volume_24h or 0)
        rank_i = int(rank or 0)
    except ValueError:
        return _entity_line(brief.entity)

    title = f"💰 {name} ({symbol})"
    parts = [title]
    if rank_i > 0:
        parts.append(f"Rank #{rank_i}")
    parts.append("")
    parts.append(f"💵 Current Price: ${price_f:,.2f}" if price_f > 0 else "💵 Current Price: unavailable")
    parts.append("")
    parts.append(f"📊 24h Change: {change_f:+.2f}% {arrow}")
    if high_f > 0 or low_f > 0:
        parts.append(f"📈 High: ${high_f:,.2f} | 📉 Low: ${low_f:,.2f}")
    parts.append("")
    market_bits: list[str] = []
    if market_cap_f > 0:
        market_bits.append(f"Cap: {_human_money(market_cap_f)}")
    if volume_f > 0:
        market_bits.append(f"Vol: {_human_money(volume_f)}")
    if market_bits:
        parts.append("💼 Market:")
        parts.append(" | ".join(market_bits))
    if brief.top_risks:
        parts.append("")
        parts.append(f"⚠️ Note: {brief.top_risks[0]}")
    return "\n".join(parts).strip() + "\n"


def _format_compact_brief_card(brief: AnalysisBrief) -> str:
    name, symbol, price, change, rank, signal_status, liquidity, top_risk, verdict = (brief.quick_verdict.split("|", 8) + ["", "", "0", "0", "0", "unknown", "0", "", ""])[:9]
    try:
        price_f = float(price or 0)
        change_f = float(change or 0)
        rank_i = int(rank or 0)
        liquidity_f = float(liquidity or 0)
    except ValueError:
        return _entity_line(brief.entity)
    arrow = "📈" if change_f > 0 else "📉" if change_f < 0 else "➖"
    parts = [f"🧩 {name} ({symbol})"]
    meta = []
    if rank_i > 0:
        meta.append(f"Rank #{rank_i}")
    if signal_status and signal_status != "unknown":
        meta.append(f"Signal: {signal_status}")
    if meta:
        parts.append(" | ".join(meta))
    parts.append("")
    if price_f > 0:
        parts.append(f"💵 Price: ${price_f:,.2f} | 24h: {change_f:+.2f}% {arrow}")
    else:
        parts.append("💵 Price: unavailable")
    if liquidity_f > 0:
        parts.append(f"💧 Liquidity: {_human_money(liquidity_f)}")
    if verdict:
        parts.append("")
        parts.append(f"⚡ {verdict}")
    if top_risk:
        parts.append(f"⚠️ Top Risk: {top_risk}")
    if not price_f and rank_i > 0:
        parts.append("📝 Quote source identified the asset correctly, but live price details were not carried into this compact brief.")
    return "\n".join(parts).strip() + "\n"


def _format_risk_card(brief: AnalysisBrief) -> str:
    name, symbol, risk_level, audit_summary, top_risk, second_risk, liquidity, signal_status, verdict = (brief.quick_verdict.split("|", 8) + ["", "", "Medium", "", "", "", "0", "unknown", ""])[:9]
    try:
        liquidity_f = float(liquidity or 0)
    except ValueError:
        liquidity_f = 0.0
    level_emoji = {"High": "🔴", "Medium": "🟠", "Low": "🟢"}.get(risk_level, "🟠")
    parts = [f"🛡️ {name} ({symbol})", f"Risk Level: {risk_level} {level_emoji}"]
    if signal_status and signal_status != "unknown":
        parts.append(f"Signal Status: {signal_status}")
    parts.append("")
    if verdict:
        parts.append(f"⚡ {verdict}")
    if top_risk:
        parts.append(f"⚠️ Top Risk: {top_risk}")
    if second_risk:
        parts.append(f"⚠️ Next Risk: {second_risk}")
    if audit_summary:
        parts.append(f"🔍 Audit: {audit_summary}")
    if liquidity_f > 0:
        parts.append(f"💧 Liquidity: {_human_money(liquidity_f)}")
    return "\n".join(parts).strip() + "\n"


def _format_audit_card(brief: AnalysisBrief) -> str:
    name, symbol, risk_level, audit_summary, top_flag, second_flag, _liquidity, gate_status, verdict = (brief.quick_verdict.split("|", 8) + ["", "", "Medium", "", "", "", "0", "warn", ""])[:9]
    gate = brief.audit_gate or gate_status.upper()
    gate_emoji = "🔴" if gate == "BLOCK" else "🟠" if gate == "WARN" else "🟢"
    level_emoji = {"High": "🔴", "Medium": "🟠", "Low": "🟢"}.get(risk_level, "🟠")
    parts = [f"🔐 {name} ({symbol})", f"Audit Gate: {gate} {gate_emoji}", f"Risk Level: {risk_level} {level_emoji}", ""]
    if verdict:
        parts.append(f"⚡ {verdict}")
    if top_flag:
        parts.append(f"⚠️ Primary Flag: {top_flag}")
    if second_flag:
        parts.append(f"⚠️ Next Flag: {second_flag}")
    if audit_summary:
        parts.append(f"🔍 Summary: {audit_summary}")
    parts.append("⚠️ This audit result is for reference only and does not constitute investment advice. Always conduct your own research.")
    return "\n".join(parts).strip() + "\n"


def _format_token_card(brief: AnalysisBrief) -> str:
    parts = [_entity_line(brief.entity)]
    if brief.audit_gate:
        gate_emoji = "🔴" if brief.audit_gate == "BLOCK" else "🟠" if brief.audit_gate == "WARN" else "🟢"
        gate_line = f"{gate_emoji} Audit Gate: {brief.audit_gate}"
        if brief.blocked_reason:
            gate_line += f" — {brief.blocked_reason}"
        parts.extend(["", gate_line])
    parts.extend(["", f"**⚡ Setup**\n{brief.quick_verdict}"])
    meta = brief.signal_quality
    if brief.conviction:
        meta = f"{brief.signal_quality} | Conviction: {brief.conviction}"
    parts.append("")
    parts.append(f"**📊 Read**\n{meta}")
    if brief.why_it_matters:
        parts.append("")
        parts.append(f"**🧠 Why**\n{brief.why_it_matters}")
    if brief.top_risks:
        parts.append("")
        parts.append("**⚠️ Risks**")
        parts.extend([f"- {item}" for item in brief.top_risks[:2]])
    if brief.what_to_watch_next:
        parts.append("")
        parts.append("**👀 Watch**")
        parts.extend([f"- {item}" for item in brief.what_to_watch_next[:2]])
    if brief.risk_tags:
        parts.append("")
        parts.append("**🏷️ Tags**")
        for tag in brief.risk_tags[:3]:
            suffix = f" — {tag.note}" if tag.note else ""
            parts.append(f"- {tag.name}: {tag.level}{suffix}")
    return "\n".join(parts).strip() + "\n"


def _format_signal_card(brief: AnalysisBrief) -> str:
    parts = [_entity_line(brief.entity)]
    if brief.audit_gate:
        gate_emoji = "🔴" if brief.audit_gate == "BLOCK" else "🟠" if brief.audit_gate == "WARN" else "🟢"
        gate_line = f"{gate_emoji} Audit Gate: {brief.audit_gate}"
        if brief.blocked_reason:
            gate_line += f" — {brief.blocked_reason}"
        parts.extend(["", gate_line])
    parts.extend(["", f"**⚡ Signal**\n{brief.quick_verdict}"])
    meta = brief.signal_quality
    if brief.conviction:
        meta = f"{brief.signal_quality} | Conviction: {brief.conviction}"
    parts.append("")
    parts.append(f"**📊 Strength**\n{meta}")
    if brief.why_it_matters:
        parts.append("")
        parts.append(f"**🧠 Why**\n{brief.why_it_matters}")
    if brief.what_to_watch_next:
        parts.append("")
        parts.append("**👀 Watch**")
        parts.extend([f"- {item}" for item in brief.what_to_watch_next[:2]])
    if brief.top_risks:
        parts.append("")
        parts.append("**⚠️ Risks**")
        parts.extend([f"- {item}" for item in brief.top_risks[:2]])
    if brief.risk_tags:
        parts.append("")
        parts.append("**🏷️ Tags**")
        for tag in brief.risk_tags[:3]:
            suffix = f" — {tag.note}" if tag.note else ""
            parts.append(f"- {tag.name}: {tag.level}{suffix}")
    return "\n".join(parts).strip() + "\n"


def _format_wallet_card(brief: AnalysisBrief) -> str:
    parts = [_entity_line(brief.entity), "", f"**⚡ Read**\n{brief.quick_verdict}"]
    if brief.why_it_matters:
        parts.append("")
        parts.append(f"**🧠 Why**\n{brief.why_it_matters}")
    if brief.top_risks:
        parts.append("")
        parts.append("**⚠️ Risks**")
        parts.extend([f"- {item}" for item in brief.top_risks[:2]])
    if brief.what_to_watch_next:
        parts.append("")
        parts.append("**👀 Watch**")
        parts.extend([f"- {item}" for item in brief.what_to_watch_next[:2]])
    return "\n".join(parts).strip() + "\n"


def _format_watchtoday_card(brief: AnalysisBrief) -> str:
    parts = [_entity_line(brief.entity), "", f"**⚡ Today**\n{brief.quick_verdict}"]
    if brief.sections:
        for section in brief.sections[:6]:
            if section.content:
                parts.append("")
                parts.append(f"**{section.title}**")
                parts.append(section.content)
    if brief.why_it_matters:
        parts.append("")
        parts.append(f"**🧠 Priority**\n{brief.why_it_matters}")
    if brief.what_to_watch_next:
        parts.append("")
        parts.append("**👀 Focus**")
        parts.extend([f"- {item}" for item in brief.what_to_watch_next[:3]])
    if brief.top_risks:
        parts.append("")
        parts.append("**⚠️ Risks**")
        parts.extend([f"- {item}" for item in brief.top_risks[:2]])
    return "\n".join(parts).strip() + "\n"


def format_brief(brief: AnalysisBrief) -> str:
    if brief.entity.startswith("Price:"):
        return _format_price_card(brief)
    if brief.entity.startswith("Brief:"):
        return _format_compact_brief_card(brief)
    if brief.entity.startswith("Risk:"):
        return _format_risk_card(brief)
    if brief.entity.startswith("Audit:"):
        return _format_audit_card(brief)
    if brief.entity.startswith("Token:"):
        return _format_token_card(brief)
    if brief.entity.startswith("Signal:"):
        return _format_signal_card(brief)
    if brief.entity.startswith("Wallet:"):
        return _format_wallet_card(brief)
    if brief.entity == "Market Watch":
        return _format_watchtoday_card(brief)

    parts = [_entity_line(brief.entity), "", brief.quick_verdict]
    return "\n".join(parts).strip() + "\n"
