from __future__ import annotations

from src.models.schemas import AnalysisBrief, RiskTag


ENTITY_EMOJI = {
    "Token:": "🪙",
    "Brief:": "🧩",
    "Price:": "💵",
    "Risk:": "🛡️",
    "Audit:": "🔐",
    "Signal:": "📡",
    "Meme:": "🚀",
    "Wallet:": "👛",
    "Portfolio:": "📂",
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


def _tree_lines(items: list[str]) -> list[str]:
    cleaned = [item.strip() for item in items if item and item.strip()]
    lines: list[str] = []
    for index, item in enumerate(cleaned):
        branch = "┗" if index == len(cleaned) - 1 else "┣"
        lines.append(f"{branch} {item}")
    return lines


def _treeify_block(text: str) -> str:
    raw_lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    if not raw_lines:
        return text

    bullet_like = []
    for line in raw_lines:
        stripped = line.strip()
        if stripped.startswith("- ") or stripped.startswith("• "):
            bullet_like.append(stripped[2:].strip())
        else:
            bullet_like.append(stripped)

    return "\n".join(_tree_lines(bullet_like))


def _tag_line(tag: RiskTag) -> str:
    suffix = f" — {tag.note}" if tag.note else ""
    return f"{tag.name}: {tag.level}{suffix}"


def _select_tags(brief: AnalysisBrief, *names: str) -> list[RiskTag]:
    wanted = {name.lower() for name in names}
    return [tag for tag in brief.risk_tags if tag.name.lower() in wanted]


def _dots(level: str | None) -> str:
    score = {
        "blocked": 1,
        "avoid": 1,
        "low": 1,
        "thin": 1,
        "unavailable": 1,
        "medium": 2,
        "moderate": 2,
        "watch": 2,
        "balanced": 3,
        "high": 3,
        "defensive": 3,
        "concentrated": 2,
    }.get(str(level or "").strip().lower(), 2)
    filled = max(0, min(4, score))
    return "".join("🟢" if i < filled else "⚪" for i in range(4)) if filled >= 3 else "".join("🟡" if i < filled else "⚪" for i in range(4))


def _arrow(change: float) -> str:
    return "📈" if change > 0 else "📉" if change < 0 else "➖"


def _short_risk(text: str) -> str:
    cleaned = (text or "").strip().rstrip(".")
    replacements = {
        "Using secondary market data for this brief": "Secondary data",
        "This is an estimated read-only snapshot, not a full PnL or cost-basis analysis": "Read-only estimate",
        "Current live wallet context is too thin to support a strong behavior judgment": "Thin payload",
        "Current live wallet evidence is limited, so this read should be treated as provisional rather than definitive": "Thin payload",
        "No matched live smart-money signal is visible on the current board, so this signal read is watchlist-only": "No smart-money follow-through",
        "There is no matched live smart-money signal on the current board, so conviction should stay capped": "No signal match",
        "No matched live smart-money signal is visible on the current board, so this token read stays capped": "No signal match",
        "Too much live token context is still missing, so this read should stay provisional": "Thin payload",
        "Live signal confirmation is still too thin to treat this as a strong setup": "Thin payload",
        "Live market quote temporarily unavailable, so this brief is using thinner fallback context": "Thin payload",
    }
    for old, new in replacements.items():
        if old.lower() in cleaned.lower():
            return new
    if "higher-beta ideas" in cleaned.lower() or "defensive" in cleaned.lower():
        return "Defensive market"
    if "liquidity" in cleaned.lower():
        return "Low liquidity" if "low" in cleaned.lower() or "thin" in cleaned.lower() else "Liquidity caution"
    if "partial" in cleaned.lower() or "limited" in cleaned.lower() or "unsupported" in cleaned.lower():
        return "Partial validity"
    if "degrad" in cleaned.lower():
        return "Degraded payload"
    return cleaned


def _brief_header(symbol: str, price: float, change: float, rank: int) -> str:
    price_text = f"${price:,.2f}" if price > 0 else "—"
    move_text = f" {change:+.2f}% {_arrow(change)}" if price > 0 else ""
    rank_text = f" #{rank}" if rank > 0 else ""
    return f"**🧩 {symbol} {price_text}{move_text}{rank_text}**"


def _signal_header(symbol: str, price: float, change: float, rank: int) -> str:
    price_text = f"${price:,.2f}" if price > 0 else "—"
    move_text = f" {change:+.2f}% {_arrow(change)}" if price > 0 else ""
    rank_text = f" #{rank}" if rank > 0 else ""
    return f"**📡 {symbol} {price_text}{move_text}{rank_text}**"


def _strength_word(value: str) -> str:
    v = (value or "").strip()
    return v.split("|", 1)[0].strip().title() if v else "Low"


def _freshness_label(note: str) -> str:
    lower = (note or "").lower()
    if "fresh" in lower:
        return f"{note.split('|',1)[1].strip() if '|' in note else note} (fresh ✅)"
    if "stale" in lower:
        return f"{note.split('|',1)[1].strip() if '|' in note else note} (stale ⚠️)"
    if "aging" in lower:
        return f"{note.split('|',1)[1].strip() if '|' in note else note} (aging ⚠️)"
    return note


def _trend_from_change(change: float, top_risk: str = "") -> str:
    if change >= 3.0:
        return "Bullish momentum"
    if change >= 1.0:
        return "Mild uptrend"
    if change >= -1.0:
        return "Neutral drift"
    if change >= -3.0:
        return "Mild downtrend"
    if change < -3.0:
        return "Bearish pressure"
    return "Defensive drift"


def _liquidity_label(liquidity: float) -> str:
    if liquidity <= 0:
        return "—"
    amount = _human_money(liquidity)
    if liquidity < 1_000_000:
        return f"{amount} ⚠️ very thin"
    if liquidity < 10_000_000:
        return f"{amount} ⚠️ thin"
    if liquidity < 50_000_000:
        return f"{amount} 🟡 moderate"
    return f"{amount} ✅ deep"


def _extract_price_tag(brief: AnalysisBrief) -> tuple[float, float, int, str]:
    header_note = next((tag.note for tag in brief.risk_tags if tag.name == "Header Market" and tag.note), "")
    price = 0.0
    change = 0.0
    rank = 0
    if header_note:
        try:
            raw_price, raw_change, raw_rank = [p.strip() for p in header_note.split("|", 2)]
            price = float(raw_price or 0)
            change = float(raw_change or 0)
            rank = int(raw_rank or 0)
        except Exception:
            pass

    note = next((tag.note for tag in brief.risk_tags if tag.name == "Binance Spot" and tag.note), "")
    if not note:
        return price, change, rank, ""
    parts = [p.strip() for p in note.split("|")]
    pair = parts[0] if parts else ""
    for part in parts[1:]:
        if part.startswith("24h"):
            try:
                change = float(part.replace("24h", "").strip().replace("%", ""))
            except ValueError:
                pass
    return price, change, rank, pair


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

    parts = [_entity_line(brief.entity)]
    asset_lines = [f"Asset: {name} ({symbol})"]
    if rank_i > 0:
        asset_lines.append(f"Rank: #{rank_i}")
    parts.extend(["", "**📁 Price**"])
    parts.extend(_tree_lines(asset_lines))

    market_lines = [f"Current Price: ${price_f:,.2f}" if price_f > 0 else "Current Price: unavailable", f"24h Change: {change_f:+.2f}% {arrow}"]
    if high_f > 0:
        market_lines.append(f"24h High: ${high_f:,.2f}")
    if low_f > 0:
        market_lines.append(f"24h Low: ${low_f:,.2f}")
    if market_cap_f > 0:
        market_lines.append(f"Market Cap: {_human_money(market_cap_f)}")
    if volume_f > 0:
        market_lines.append(f"24h Volume: {_human_money(volume_f)}")
    parts.extend(["", "**📊 Market**"])
    parts.extend(_tree_lines(market_lines))

    source_tags = _select_tags(brief, "source", "binance spot")
    if source_tags:
        parts.extend(["", "**🏷️ Context**"])
        parts.extend(_tree_lines([_tag_line(tag) for tag in source_tags[:2]]))

    if brief.top_risks:
        parts.extend(["", "**🧠 Source Note**"])
        parts.extend(_tree_lines([brief.top_risks[0]]))
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

    signal_map = {
        "unmatched": "No clear entry",
        "watch": "Watching — early setup",
        "bullish": "Watching — early setup",
        "triggered": "Active follow-through",
        "unknown": "No clear entry",
    }
    trend = _trend_from_change(change_f, top_risk)
    liquidity_text = _liquidity_label(liquidity_f)
    confidence = brief.signal_quality or "Low"

    parts = [_brief_header(symbol or name, price_f, change_f, rank_i)]
    parts.extend(["", "**⚡ Snapshot**"])
    parts.extend(_tree_lines([
        f"Signal: {signal_map.get((signal_status or '').lower(), signal_status.title() or 'No clear entry')}",
        f"Trend: {trend}",
        f"Liquidity: {liquidity_text}",
    ]))
    parts.extend(["", f"**🧠 Verdict {_dots(confidence)}**\n{verdict or 'Monitor only. No conviction setup visible.'}"])
    footer_bits = [_short_risk(top_risk or 'Secondary data')]
    source_tag = next((tag for tag in brief.risk_tags if tag.name == 'Source' and tag.note), None)
    if source_tag and source_tag.note == 'Secondary market data':
        footer_bits.append('Thin context' if price_f <= 0 or liquidity_f <= 0 else 'Market-only read')
    elif liquidity_f <= 0:
        footer_bits.append('Thin liquidity')
    parts.extend(["", f"**⚠️ {' · '.join(list(dict.fromkeys(footer_bits))[:2])}**"])
    return "\n".join(parts).strip() + "\n"


def _format_risk_card(brief: AnalysisBrief) -> str:
    name, symbol, risk_level, audit_summary, top_risk, second_risk, liquidity, signal_status, verdict = (brief.quick_verdict.split("|", 8) + ["", "", "Medium", "", "", "", "0", "unknown", ""])[:9]
    try:
        liquidity_f = float(liquidity or 0)
    except ValueError:
        liquidity_f = 0.0
    level_emoji = {"High": "🔴", "Medium": "🟠", "Low": "🟢"}.get(risk_level, "🟠")
    parts = [_entity_line(brief.entity), "", "**📁 Risk**"]
    risk_lines = [f"Asset: {name} ({symbol})", f"Risk Level: {risk_level} {level_emoji}"]
    if signal_status and signal_status != "unknown":
        risk_lines.append(f"Signal Status: {signal_status}")
    parts.extend(_tree_lines(risk_lines))

    if verdict:
        parts.extend(["", f"**⚡ Read**\n{verdict}"])
    if top_risk or second_risk:
        parts.extend(["", "**⚠️ Main Risks**"])
        parts.extend(_tree_lines([item for item in [top_risk, second_risk] if item]))

    context_lines = []
    if audit_summary:
        context_lines.append(f"Audit: {audit_summary}")
    if liquidity_f > 0:
        context_lines.append(f"Visible Liquidity: {_human_money(liquidity_f)}")
    if context_lines:
        parts.extend(["", "**🏷️ Context**"])
        parts.extend(_tree_lines(context_lines))
    return "\n".join(parts).strip() + "\n"


def _format_audit_card(brief: AnalysisBrief) -> str:
    name, symbol, risk_level, audit_summary, top_flag, second_flag, third_flag, gate_status, verdict = (brief.quick_verdict.split("|", 8) + ["", "", "Medium", "", "", "", "", "warn", ""])[:9]
    gate = (brief.audit_gate or gate_status.upper() or "WARN").upper()
    gate_word = "Avoid" if gate == "BLOCK" else "Warn" if gate == "WARN" else "Allow"
    findings = [item for item in [top_flag, second_flag, third_flag] if item][:3]
    if not findings:
        findings = ["Contract: No red flags", "Liquidity: Adequate", "Structure: Stable"]

    parts = [f"**🔐 {symbol} Audit: {'🔴' if gate == 'BLOCK' else '🟠' if gate == 'WARN' else '🟢'} {gate_word} Risk: {risk_level}**"]
    parts.extend(["", "**⚡ Findings**"])
    parts.extend(_tree_lines(findings[:3]))

    meme_sections = [section for section in brief.sections if section.title == "🧪 Meme Lens" and section.content.strip()]
    if meme_sections:
        parts.extend(["", "**🧪 Meme Lens**"])
        parts.append(_treeify_block(meme_sections[0].content))

    parts.extend(["", f"**🧠 Verdict {_dots(risk_level if gate != 'BLOCK' else 'Low')}**\n{verdict}"])
    footer_bits = []
    validity = next((tag for tag in brief.risk_tags if tag.name == "Audit Validity"), None)
    if validity and validity.level.lower() == "limited":
        footer_bits.append("Partial validity")
    if "degrad" in audit_summary.lower():
        footer_bits.append("Degraded payload")
    footer_bits.append("Not investment advice")
    parts.extend(["", f"**⚠️ {' · '.join(footer_bits)}**"])
    return "\n".join(parts).strip() + "\n"


def _format_token_card(brief: AnalysisBrief) -> str:
    symbol = brief.entity.replace("Token:", "").strip()
    price_f, change_f, rank_i, pair = _extract_price_tag(brief)
    liquidity_f = 0.0
    try:
        liquidity_f = float((brief.why_it_matters or '').split('liquidity ')[1].split()[0]) if 'liquidity ' in (brief.why_it_matters or '').lower() else 0.0
    except Exception:
        liquidity_f = 0.0
    gate = brief.audit_gate or "WARN"
    signal_word = "No clear entry"
    lower_why = (brief.why_it_matters or "").lower()
    if "smart-money wallets" in lower_why:
        signal_word = "Watching — early setup"
    if gate == "BLOCK":
        signal_word = "Blocked"

    trend = _trend_from_change(change_f)
    liquidity_tag = next((tag for tag in brief.risk_tags if tag.name == "Binance Spot"), None)
    liquidity_text = _liquidity_label(liquidity_f)
    if pair and liquidity_f <= 0:
        liquidity_text = pair
    if liquidity_tag and liquidity_tag.note and "spread" in liquidity_tag.note.lower() and liquidity_f <= 0:
        liquidity_text = liquidity_tag.note.split("|")[0].strip()

    parts = [_brief_header(symbol, price_f, change_f, rank_i)]
    parts.extend(["", "**⚡ Snapshot**"])
    parts.extend(_tree_lines([
        f"Signal: {signal_word}",
        f"Trend: {trend}",
        f"Liquidity: {liquidity_text}",
    ]))
    if brief.beginner_note and "research summary" not in brief.beginner_note.lower():
        ownership_title = "**💼 Ownership**" if any(line.startswith(("Holders:", "Smart money:", "Top-10 concentration:")) for line in brief.beginner_note.splitlines()) else "**💼 Top Holdings**"
        parts.extend(["", ownership_title])
        parts.extend(_tree_lines(brief.beginner_note.splitlines()[:3]))
    verdict_text = brief.quick_verdict
    parts.extend(["", f"**🧠 Verdict {_dots(brief.signal_quality)}**\n{verdict_text}"])
    risk_bits = [_short_risk(risk) for risk in brief.top_risks[:2]] or ["Thin payload"]
    parts.extend(["", f"**⚠️ {' · '.join(risk_bits[:2])}**"])
    return "\n".join(parts).strip() + "\n"


def _format_signal_card(brief: AnalysisBrief) -> str:
    symbol = brief.entity.replace("Signal:", "").strip()
    price_f, change_f, rank_i, _pair = _extract_price_tag(brief)
    gate = (brief.audit_gate or "WARN").title()
    invalidation_tags = [tag for tag in brief.risk_tags if tag.name == "Invalidation" and tag.note]
    invalidation = invalidation_tags[0].note if invalidation_tags else "Needs confirmation"
    entry_zone = next((tag.note for tag in brief.risk_tags if tag.name == "Entry Zone" and tag.note), "")
    timing = next((tag.note for tag in brief.risk_tags if tag.name == "Signal Timing" and tag.note), "")
    exit_pressure = next((tag.note for tag in brief.risk_tags if tag.name == "Exit Pressure" and tag.note), "")
    strength_line = _strength_word(brief.signal_quality)
    if exit_pressure:
        exit_pct = exit_pressure.replace("Exit rate ", "").strip()
        strength_line = f"{strength_line} · {exit_pct} exited ⚠️" if exit_pct else strength_line

    setup_lines = [f"Audit: {'🔴' if gate.lower() == 'block' else '🟠' if gate.lower() == 'warn' else '🟢'} {gate}"]
    if entry_zone:
        setup_lines.append(f"Entry zone: {entry_zone}")
    setup_lines.append(f"Strength: {strength_line}")
    if timing:
        setup_lines.append(f"Signal age: {_freshness_label(timing)}")
    setup_lines.append(f"Invalidation: {_short_risk(invalidation)}")

    parts = [_signal_header(symbol, price_f, change_f, rank_i)]
    parts.extend(["", "**⚡ Setup**"])
    parts.extend(_tree_lines(setup_lines))
    parts.extend(["", f"**🧠 Verdict {_dots(brief.signal_quality)}**\n{brief.quick_verdict}"])
    risk_bits = [_short_risk(risk) for risk in brief.top_risks[:2]] or ["Thin payload"]
    if any("late setup" in (risk or "").lower() for risk in brief.top_risks[:2]) and "Most wallets already exited" not in risk_bits:
        risk_bits.insert(0, "Most wallets already exited")
    parts.extend(["", f"**⚠️ {' · '.join(risk_bits[:2])}**"])
    return "\n".join(parts).strip() + "\n"


def _format_wallet_card(brief: AnalysisBrief) -> str:
    follow_tag = next((tag for tag in brief.risk_tags if tag.name == "Follow Verdict"), None)
    follow = follow_tag.note if follow_tag and follow_tag.note else "Unknown"
    follow_emoji = "✅" if follow == "Track" else "⚠️" if follow == "Unknown" else "❌"
    address = brief.entity.replace("Wallet:", "").strip()
    short_address = address if len(address) <= 10 else f"{address[:6]}…{address[-5:]}"

    behavior_lines = []
    thin_wallet = any("thin" in (risk or "").lower() for risk in brief.top_risks[:2]) or "too thin" in (brief.quick_verdict or "").lower()
    watch = brief.what_to_watch_next[:3]
    lead_holding = next((tag.note for tag in brief.risk_tags if tag.name == "Lead Holding" and tag.note), "")
    concentration = next((tag.note for tag in brief.risk_tags if tag.name == "Concentration Risk" and tag.note), "")
    activity = next((tag.note for tag in brief.risk_tags if tag.name == "Activity" and tag.note), "")
    if thin_wallet:
        behavior_lines = ["Activity: Static", "Top move: No rotation visible", "Drift: No change detected"]
    elif lead_holding or concentration or activity:
        behavior_lines = [
            f"Activity: {activity or 'Visible'}",
            f"Top move: {lead_holding or 'Lead holding visible'}",
            f"Drift: {concentration or 'Concentration controlled'}",
        ]
    elif watch:
        labels = ["Activity", "Top move", "Drift"]
        for idx, item in enumerate(watch[:3]):
            cleaned = item.replace('whether ', '').replace('the wallet ', '').rstrip('.')
            behavior_lines.append(f"{labels[idx]}: {cleaned}")
    else:
        behavior_lines = ["Activity: Static", "Top move: No rotation visible", "Drift: No change detected"]

    parts = [f"**👛 {short_address} {follow_emoji} {follow}**"]
    parts.extend(["", "**⚡ Behavior**"])
    parts.extend(_tree_lines(behavior_lines[:3]))
    dot_level = "Low" if follow == "Unknown" else "Medium" if follow == "Track" else "Low"
    parts.extend(["", f"**🧠 Verdict {_dots(dot_level)}**\n{brief.quick_verdict}"])
    risk_bits = [_short_risk(risk) for risk in brief.top_risks[:2]] or ["Thin payload"]
    risk_bits = ["Thin payload" if "thin" in bit.lower() or "wallet payload" in bit.lower() else bit for bit in risk_bits]
    if follow == "Unknown" and "not a follow signal" not in " ".join(risk_bits).lower():
        risk_bits.append("Not a follow signal")
    parts.extend(["", f"**⚠️ {' · '.join(risk_bits[:2])}**"])
    return "\n".join(parts).strip() + "\n"


def _runtime_banner(brief: AnalysisBrief) -> list[str]:
    if brief.runtime_state == "live_degraded" and brief.runtime_warning:
        return ["", f"**🛠️ Runtime**\n{brief.runtime_warning}"]
    if brief.runtime_state == "mock":
        return ["", "**🛠️ Runtime**\nRunning in mock mode."]
    return []


def _format_watchtoday_card(brief: AnalysisBrief) -> str:
    parts = ["**🌐 Watchtoday**"]
    parts.extend(_runtime_banner(brief))

    signals = next((section for section in brief.sections if "Smart Money Flow" in section.title or "Signal" in section.title), None)
    attention = next((section for section in brief.sections if "Trending Now" in section.title), None)

    if signals and signals.content:
        parts.extend(["", "**⚡ Signals**"])
        parts.append(_treeify_block(signals.content))
    if attention and attention.content:
        parts.extend(["", "**🔥 Attention**"])
        parts.append(_treeify_block(attention.content))

    board_verdict = brief.quick_verdict
    lower_board = board_verdict.lower()
    if "opportunity exists" in lower_board and "selectivity matters" in lower_board:
        board_verdict = "Moderate board. Be selective."
    elif "selective rather than defensive" in lower_board or "selectively instead of defensively" in lower_board:
        board_verdict = "Moderate board. Be selective."
    elif len(board_verdict) > 90:
        board_verdict = board_verdict.split(". ", 1)[0].rstrip(".") + "."
    parts.extend(["", f"**🧠 Board {_dots(brief.signal_quality)}**\n{board_verdict}"])
    risk_bits = [_short_risk(risk) for risk in brief.top_risks[:2]] or ["Attention ≠ signal"]
    if len(risk_bits) >= 2:
        left, right = risk_bits[0], risk_bits[1]
        left_token = left.split()[0].rstrip(':') if left else ''
        right_token = right.split()[0].rstrip(':') if right else ''
        if left_token and left_token == right_token:
            merged_tail = []
            if "concentration" in left.lower() or "holder" in left.lower():
                merged_tail.append("concentration")
            if "audit" in left.lower() or "caution" in left.lower():
                merged_tail.append("audit ⚠️")
            if "concentration" in right.lower() or "holder" in right.lower():
                merged_tail.append("concentration")
            if "audit" in right.lower() or "caution" in right.lower():
                merged_tail.append("audit ⚠️")
            dedup_tail = []
            for item in merged_tail:
                if item not in dedup_tail:
                    dedup_tail.append(item)
            risk_bits = [f"{left_token}: {' + '.join(dedup_tail)}"] if dedup_tail else [left]
    if attention and signals:
        risk_bits.insert(0, "Attention ≠ signal")
    parts.extend(["", f"**⚠️ {' · '.join(dict.fromkeys(risk_bits))}**"])
    return "\n".join(parts).strip() + "\n"


def _format_portfolio_card(brief: AnalysisBrief) -> str:
    total_value = ""
    why = brief.why_it_matters or ""
    marker = "Estimated visible Spot value is about $"
    if marker in why:
        total_value = why.split(marker, 1)[1].split(" ", 1)[0].rstrip(".")

    stable_tag = next((tag for tag in brief.risk_tags if tag.name == "Stablecoin Share" and tag.note), None)
    concentration_tag = next((tag for tag in brief.risk_tags if tag.name == "Top Concentration" and tag.note), None)
    top_lines = brief.beginner_note.splitlines()[:3] if brief.beginner_note else []
    top_asset = top_lines[0].split("~", 1)[0].strip() if top_lines else "—"
    posture = brief.signal_quality or "Defensive"
    risk_pct = "—"
    if "risk assets are " in why:
        try:
            risk_pct = why.split("risk assets are ", 1)[1].split("%", 1)[0] + "%"
        except Exception:
            pass

    parts = [f"**📂 Holdings Binance Spot {'~$' + total_value if total_value else ''}**".rstrip()]
    parts.extend(["", "**⚡ Posture**"])
    parts.extend(_tree_lines([
        f"Stables: {stable_tag.note} 💵" if stable_tag else "Stables: —",
        f"Risk: {risk_pct}",
        f"Top asset: {top_asset}",
    ]))
    if top_lines:
        parts.extend(["", "**💼 Top Holdings**"])
        parts.extend(_tree_lines(top_lines))
    parts.extend(["", f"**🧠 Verdict {_dots(posture)}**\n{brief.quick_verdict}"])
    freshness = next((tag.note for tag in brief.risk_tags if tag.name == "Freshness" and tag.note), "")
    footer_bits = [f"Snapshot {freshness}" if freshness else "Read-only estimate", "Read-only estimate"]
    parts.extend(["", f"**⚠️ {' · '.join(list(dict.fromkeys(footer_bits))[:2])}**"])
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
    if brief.entity.startswith("Meme:"):
        return _format_token_card(brief)
    if brief.entity.startswith("Token:"):
        return _format_token_card(brief)
    if brief.entity.startswith("Signal:"):
        return _format_signal_card(brief)
    if brief.entity.startswith("Wallet:"):
        return _format_wallet_card(brief)
    if brief.entity.startswith("Portfolio:"):
        return _format_portfolio_card(brief)
    if brief.entity == "Market Watch":
        return _format_watchtoday_card(brief)

    parts = [_entity_line(brief.entity), "", brief.quick_verdict]
    return "\n".join(parts).strip() + "\n"
