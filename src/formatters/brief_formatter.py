from __future__ import annotations

from src.models.schemas import AnalysisBrief


ENTITY_EMOJI = {
    "Token:": "🪙",
    "Price:": "💵",
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

    title = f"💰 [{name}](<{link}>) ({symbol})" if link else f"💰 {name} ({symbol})"
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
    return "\n".join(parts).strip() + "\n"


def format_brief(brief: AnalysisBrief) -> str:
    if brief.entity.startswith("Price:"):
        return _format_price_card(brief)

    parts: list[str] = []
    parts.append(_entity_line(brief.entity))
    parts.append("")
    parts.append("**⚡ Quick Verdict**")
    parts.append(brief.quick_verdict)
    parts.append("")
    parts.append("**📊 Signal Quality**")
    parts.append(brief.signal_quality)
    parts.append("")
    parts.append("**⚠️ Top Risks**")
    if brief.top_risks:
        parts.extend([f"- {item}" for item in brief.top_risks])
    else:
        parts.append("- No major risks identified yet; still requires normal caution.")
    parts.append("")
    parts.append("**🧠 Why It Matters**")
    parts.append(brief.why_it_matters)
    parts.append("")
    parts.append("**👀 What To Watch Next**")
    if brief.what_to_watch_next:
        parts.extend([f"- {item}" for item in brief.what_to_watch_next])
    else:
        parts.append("- Watch for confirmation, liquidity, and follow-through.")

    if brief.risk_tags:
        parts.append("")
        parts.append("**🏷️ Risk Tags**")
        for tag in brief.risk_tags:
            suffix = f" — {tag.note}" if tag.note else ""
            parts.append(f"- {tag.name}: {tag.level}{suffix}")

    if brief.conviction:
        parts.append("")
        parts.append("**🎯 Conviction**")
        parts.append(brief.conviction)

    if brief.beginner_note:
        parts.append("")
        parts.append("**🌱 Beginner Note**")
        parts.append(brief.beginner_note)

    return "\n".join(parts).strip() + "\n"
