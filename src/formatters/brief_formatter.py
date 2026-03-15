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
            return f"{emoji} {entity}"
    return f"📌 {entity}"


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


def _section_content(brief: AnalysisBrief, *keywords: str) -> str:
    lowered = [keyword.lower() for keyword in keywords]
    for section in brief.sections:
        title = (section.title or "").lower()
        if any(keyword in title for keyword in lowered):
            return section.content or ""
    return ""


def _placeholder_tree(*items: str) -> str:
    return "\n".join(_tree_lines([item for item in items if item and item.strip()]))


def _tag_line(tag: RiskTag) -> str:
    suffix = f" — {tag.note}" if tag.note else ""
    return f"{tag.name}: {tag.level}{suffix}"


def _select_tags(brief: AnalysisBrief, *names: str) -> list[RiskTag]:
    wanted = {name.lower() for name in names}
    return [tag for tag in brief.risk_tags if tag.name.lower() in wanted]


def _first_tag(brief: AnalysisBrief, *names: str) -> RiskTag | None:
    tags = _select_tags(brief, *names)
    return tags[0] if tags else None


def _tag_note(brief: AnalysisBrief, *names: str) -> str:
    tag = _first_tag(brief, *names)
    return tag.note if tag and tag.note else ""


def _note_lines(note: str) -> list[str]:
    return [part.strip() for part in note.split(" | ") if part and part.strip()]


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


def _is_operator_runtime_note(text: str) -> bool:
    lower = (text or "").strip().lower()
    return any([
        "bridge is enabled" in lower,
        "live token/signal/audit bridge" in lower,
        "live watchtoday bridge" in lower,
        "live wallet bridge" in lower,
        "live audit bridge" in lower,
        "live signal bridge" in lower,
    ])


def _short_risk(text: str) -> str:
    cleaned = (text or "").strip().rstrip(".")
    if _is_operator_runtime_note(cleaned):
        return ""
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
        "Live bridge is unavailable for token; using degraded context": "Live context limited",
        "Live bridge is unavailable for signal; using degraded context": "Live context limited",
        "Live bridge is unavailable for wallet; using degraded context": "Live context limited",
        "Live bridge is unavailable for audit; using degraded context": "Live context limited",
        "Live bridge is unavailable for watchtoday; using degraded context": "Live context limited",
        "Runtime detail: HTTP live mode requires the optional dependency 'httpx'. Install requirements.txt or use file:// live mode": "Runtime dependency missing",
        "Portfolio concentration is already high, so any new idea should clear a higher bar than usual": "High portfolio concentration",
    }
    for old, new in replacements.items():
        if old.lower() in cleaned.lower():
            return new
    if cleaned.lower() == "live bridge limited":
        return "Live context limited"
    if "higher-beta ideas" in cleaned.lower() or "defensive" in cleaned.lower():
        return "Defensive market"
    if "user reported" in cleaned.lower() or "reported as risky by users" in cleaned.lower():
        return "User-reported risk"
    if "contract upgradeable" in cleaned.lower():
        return "Upgradeable contract"
    if "honeypot" in cleaned.lower():
        return "Honeypot risk"
    if "scam risk" in cleaned.lower():
        return "Scam risk"
    if "contract risk" in cleaned.lower():
        return "Contract risk"
    if "liquidity" in cleaned.lower():
        return "Low liquidity" if "low" in cleaned.lower() or "thin" in cleaned.lower() else "Liquidity caution"
    if "too many daily market lanes are still sparse" in cleaned.lower():
        return "Sparse lane coverage"
    if "no clean smart-money setup yet" in cleaned.lower():
        return "No clean board leader yet"
    if "coverage is thin" in cleaned.lower():
        return "Attention is limited"
    if "partial" in cleaned.lower() or "limited" in cleaned.lower() or "unsupported" in cleaned.lower():
        return "Limited live context"
    if "httpx" in cleaned.lower() or "optional dependency" in cleaned.lower():
        return "Runtime dependency missing"
    if "could not reach the upstream live bridge" in cleaned.lower():
        return "Using reduced live coverage"
    if "live bridge limited" in cleaned.lower() or "live bridge is unavailable" in cleaned.lower():
        return "Live context limited"
    if "degrad" in cleaned.lower():
        return "Live context limited"
    return cleaned


def _brief_header(symbol: str, price: float, change: float, rank: int) -> str:
    price_text = f"${price:,.2f}" if price > 0 else "—"
    move_text = f" {change:+.2f}% {_arrow(change)}" if price > 0 else ""
    rank_text = f" #{rank}" if rank > 0 else ""
    return f"🧩 {symbol} {price_text}{move_text}{rank_text}"


def _signal_header(symbol: str, price: float, change: float, rank: int) -> str:
    price_text = f"${price:,.2f}" if price > 0 else "—"
    move_text = f" {change:+.2f}% {_arrow(change)}" if price > 0 else ""
    rank_text = f" #{rank}" if rank > 0 else ""
    return f"📡 {symbol} {price_text}{move_text}{rank_text}"


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
    lower_risk = (top_risk or "").lower()
    if "thin payload" in lower_risk or "runtime dependency missing" in lower_risk or "live bridge limited" in lower_risk or "optional dependency" in lower_risk or "httpx" in lower_risk:
        return "Limited read"
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
    parts.extend(["", "📁 Price"])
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
    parts.extend(["", "📊 Market"])
    parts.extend(_tree_lines(market_lines))

    source_tags = _select_tags(brief, "source", "binance spot")
    if source_tags:
        parts.extend(["", "🏷️ Context"])
        parts.extend(_tree_lines([_tag_line(tag) for tag in source_tags[:2]]))

    if brief.top_risks:
        parts.extend(["", "🧠 Source Note"])
        parts.extend(_tree_lines([brief.top_risks[0]]))
    return "\n".join(parts).strip() + "\n"


def _format_compact_brief_card(brief: AnalysisBrief) -> str:
    fields = brief.quick_verdict.split("|")
    name, symbol, price, change, rank, signal_status, liquidity, top_risk, verdict, volume_24h, market_cap, smart_money_count, kline_trend = (
        fields + ["", "", "0", "0", "0", "unknown", "0", "", "", "0", "0", "0", ""]
    )[:13]
    try:
        price_f = float(price or 0)
        change_f = float(change or 0)
        rank_i = int(rank or 0)
        liquidity_f = float(liquidity or 0)
        volume_f = float(volume_24h or 0)
        market_cap_f = float(market_cap or 0)
        smart_money_count_i = int(float(smart_money_count or 0))
    except ValueError:
        return _entity_line(brief.entity)

    signal_map = {
        "unmatched": "Signal not confirmed",
        "watch": "Watching — early setup",
        "bullish": "Watching — early setup",
        "triggered": "Active follow-through",
        "active": "Active follow-through",
        "unknown": "Signal not confirmed",
    }
    trend = _trend_from_change(change_f, top_risk)
    if kline_trend.strip() and trend != "Limited read":
        trend = f"K-line {kline_trend.strip()}"
    if price_f <= 0 or liquidity_f <= 0:
        trend = "Limited read"
    liquidity_text = _liquidity_label(liquidity_f)
    if liquidity_f <= 0 and liquidity_text == "—":
        liquidity_text = "— limited"
    confidence = brief.signal_quality or "Low"
    signal_line = signal_map.get((signal_status or "").lower(), signal_status.title() or "No clear entry")
    if smart_money_count_i > 0:
        if (signal_status or "").lower() in {"triggered", "active", "bullish"}:
            signal_line = f"Active follow-through · {smart_money_count_i} wallet{'s' if smart_money_count_i != 1 else ''}"
        else:
            signal_line = f"{signal_line} · {smart_money_count_i} wallet{'s' if smart_money_count_i != 1 else ''}"

    source_tag = next((tag for tag in brief.risk_tags if tag.name == 'Source' and tag.note), None)
    maturity_tag = _first_tag(brief, 'Maturity')
    order_book_tag = _first_tag(brief, 'Order Book')
    spot_tag = _first_tag(brief, 'Binance Spot')

    parts = [_brief_header(symbol or name, price_f, change_f, rank_i)]
    parts.extend(["", "⚡ Snapshot"])
    parts.extend(_tree_lines([
        f"Signal: {signal_line}",
        f"Trend: {trend}",
        f"Liquidity: {liquidity_text}",
    ]))

    market_lines = []
    if volume_f > 0:
        market_lines.append(f"Volume 24h: {_human_money(volume_f)}")
    if market_cap_f > 0:
        market_lines.append(f"Market Cap: {_human_money(market_cap_f)}")
    if smart_money_count_i > 0:
        market_lines.append(f"Smart money: {smart_money_count_i} wallets")
    holders_tag = _first_tag(brief, 'Holders')
    if holders_tag and holders_tag.note:
        market_lines.append(f"Holders: {holders_tag.note}")
    if market_lines:
        parts.extend(["", "📊 Market"])
        parts.extend(_tree_lines(market_lines))

    ownership_lines = []
    ownership_tag = _first_tag(brief, 'Ownership')
    sm_holders_tag = _first_tag(brief, 'Smart Money Holders')
    sm_holding_pct_tag = _first_tag(brief, 'Smart Money Holding %')
    kline_tag = _first_tag(brief, 'K-line')
    if ownership_tag and ownership_tag.note:
        ownership_lines.append(ownership_tag.note.replace('Top-10 concentration ', 'Top-10 concentration: '))
    if sm_holders_tag and sm_holders_tag.note:
        ownership_lines.append(f"Smart money holders: {sm_holders_tag.note}")
    if sm_holding_pct_tag and sm_holding_pct_tag.note:
        ownership_lines.append(f"Smart money holding: {sm_holding_pct_tag.note}")
    if kline_tag and kline_tag.note:
        ownership_lines.append(f"K-line: {kline_tag.note}")
    if ownership_lines:
        parts.extend(["", "💼 Structure"])
        parts.extend(_tree_lines(ownership_lines[:4]))

    read_lines = []
    if spot_tag and spot_tag.note:
        read_lines.append(f"Spot: {spot_tag.note}")
    if order_book_tag and order_book_tag.note:
        read_lines.append(f"Order book: {order_book_tag.note}")
    if maturity_tag and maturity_tag.note:
        read_lines.append(f"Maturity: {maturity_tag.note}")
    if source_tag and source_tag.note and source_tag.note != 'Secondary market data':
        read_lines.append(f"Source: {source_tag.note}")
    if read_lines:
        parts.extend(["", "🔎 Read"])
        parts.extend(_tree_lines(read_lines[:4]))

    parts.extend(["", f"🧠 Verdict {_dots(confidence)}\n{verdict or 'Monitor only. No conviction setup visible.'}"])
    footer_bits = [_short_risk(top_risk or 'Secondary data')]
    if source_tag and source_tag.note == 'Secondary market data':
        footer_bits.append('Thin context' if price_f <= 0 or liquidity_f <= 0 else 'Market-only read')
    elif liquidity_f <= 0 and _short_risk(top_risk or '').lower() != 'thin payload':
        footer_bits.append('Thin liquidity')
    parts.extend(["", f"⚠️ {' · '.join(list(dict.fromkeys(footer_bits))[:2])}"])
    return "\n".join(parts).strip() + "\n"


def _format_risk_card(brief: AnalysisBrief) -> str:
    name, symbol, risk_level, audit_summary, top_risk, second_risk, liquidity, signal_status, verdict = (brief.quick_verdict.split("|", 8) + ["", "", "Medium", "", "", "", "0", "unknown", ""])[:9]
    try:
        liquidity_f = float(liquidity or 0)
    except ValueError:
        liquidity_f = 0.0
    level_emoji = {"High": "🔴", "Medium": "🟠", "Low": "🟢"}.get(risk_level, "🟠")
    parts = [_entity_line(brief.entity), "", "📁 Risk"]
    risk_lines = [f"Asset: {name} ({symbol})", f"Risk Level: {risk_level} {level_emoji}"]
    if signal_status and signal_status != "unknown":
        risk_lines.append(f"Signal Status: {signal_status}")
    parts.extend(_tree_lines(risk_lines))

    if verdict:
        parts.extend(["", f"⚡ Read\n{verdict}"])
    if top_risk or second_risk:
        parts.extend(["", "⚠️ Main Risks"])
        parts.extend(_tree_lines([item for item in [top_risk, second_risk] if item]))

    context_lines = []
    if audit_summary:
        context_lines.append(f"Audit: {audit_summary}")
    if liquidity_f > 0:
        context_lines.append(f"Visible Liquidity: {_human_money(liquidity_f)}")
    if context_lines:
        parts.extend(["", "🏷️ Context"])
        parts.extend(_tree_lines(context_lines))
    return "\n".join(parts).strip() + "\n"


def _format_audit_card(brief: AnalysisBrief) -> str:
    name, symbol, risk_level, audit_summary, top_flag, second_flag, third_flag, gate_status, verdict = (brief.quick_verdict.split("|", 8) + ["", "", "Medium", "", "", "", "", "warn", ""])[:9]
    gate = (brief.audit_gate or gate_status.upper() or "WARN").upper()
    gate_word = "Avoid" if gate == "BLOCK" else "Warn" if gate == "WARN" else "Allow"
    findings = [item for item in [top_flag, second_flag, third_flag] if item][:3]
    if not findings:
        findings = ["Contract: —", "Liquidity: —", "Structure: —"]

    parts = [f"🔐 {symbol} Audit: {'🔴' if gate == 'BLOCK' else '🟠' if gate == 'WARN' else '🟢'} {gate_word} Risk: {risk_level}"]
    parts.extend(["", "⚡ Findings"])
    parts.extend(_tree_lines(findings[:3]))

    market_content = _section_content(brief, "market context")
    if market_content.strip():
        parts.extend(["", "📊 Market Context"])
        parts.append(_treeify_block(market_content))

    meme_content = _section_content(brief, "meme lens")
    if meme_content.strip():
        parts.extend(["", "🧪 Meme Lens"])
        parts.append(_treeify_block(meme_content))

    signal_content = _section_content(brief, "signal lens")
    if signal_content.strip():
        parts.extend(["", "📡 Signal Lens"])
        parts.append(_treeify_block(signal_content))

    verdict_text = verdict or "Partial read. Stay cautious."
    parts.extend(["", f"🧠 Verdict {_dots(risk_level if gate != 'BLOCK' else 'Low')}\n{verdict_text}"])
    footer_bits = []
    validity = next((tag for tag in brief.risk_tags if tag.name == "Audit Validity"), None)
    if validity and validity.level.lower() == "limited":
        footer_bits.append("Limited audit visibility")
    if "degrad" in audit_summary.lower():
        footer_bits.append("Degraded payload")
    footer_bits.append("Not investment advice")
    parts.extend(["", f"⚠️ {' · '.join(footer_bits)}"])
    return "\n".join(parts).strip() + "\n"


def _format_token_card(brief: AnalysisBrief) -> str:
    symbol = brief.entity.replace("Token:", "").strip()
    price_f, change_f, rank_i, pair = _extract_price_tag(brief)
    gate = brief.audit_gate or "WARN"
    signal_word = "Signal not confirmed"
    lower_why = (brief.why_it_matters or "").lower()
    lower_verdict = (brief.quick_verdict or "").lower()
    if gate == "BLOCK" or "blocked" in lower_verdict:
        signal_word = "Blocked"
    elif "no signal match" in lower_verdict or "unmatched" in lower_why or "no matched smart-money signal" in lower_why:
        signal_word = "No signal match"
    elif "monitor only" in lower_verdict and ("active pricing" in lower_why or price_f > 0):
        signal_word = "Market active · setup absent"
    elif "active but late" in lower_verdict:
        signal_word = "Active — late setup"
    elif "active setup" in lower_verdict:
        signal_word = "Active follow-through"
    elif "stale setup" in lower_verdict:
        signal_word = "Stale setup"
    elif "early setup" in lower_verdict or "smart-money wallets" in lower_why or "signal timing" in lower_why or "signal is" in lower_why:
        signal_word = "Watching — early setup"

    trend = _trend_from_change(change_f)
    liquidity_tag = next((tag for tag in brief.risk_tags if tag.name == "Binance Spot"), None)
    explicit_liquidity_tag = _first_tag(brief, "Liquidity")
    liquidity_text = "—"
    if explicit_liquidity_tag and explicit_liquidity_tag.note:
        note = explicit_liquidity_tag.note.replace("Visible liquidity ", "").strip()
        numeric = note.replace(",", "")
        liquidity_text = _human_money(float(numeric)) if numeric.replace(".", "").isdigit() else note
    elif pair:
        liquidity_text = pair
    if liquidity_tag and liquidity_tag.note and "spread" in liquidity_tag.note.lower() and not explicit_liquidity_tag:
        liquidity_text = liquidity_tag.note.split("|")[0].strip()
    if liquidity_text == "—":
        liquidity_text = "— limited"
    momentum_note = _tag_note(brief, "Momentum")
    market_note = _tag_note(brief, "Market Data")

    parts = [_brief_header(symbol, price_f, change_f, rank_i)]
    parts.extend(["", "⚡ Snapshot"])
    snapshot_lines = [
        f"Signal: {signal_word}",
        f"Trend: {trend if price_f > 0 else '— limited'}",
        f"Liquidity: {liquidity_text}",
    ]
    if momentum_note:
        snapshot_lines.append(f"Momentum: {momentum_note}")
    parts.extend(_tree_lines(snapshot_lines))

    ownership_lines: list[str] = []
    if brief.beginner_note and "research summary" not in brief.beginner_note.lower():
        ownership_lines = [line for line in brief.beginner_note.splitlines()[:5] if line.strip()]
    ownership_tag = next((tag for tag in brief.risk_tags if tag.name == "Ownership" and tag.note), None)
    if ownership_tag and not any(line.startswith("Top-10 concentration:") for line in ownership_lines):
        ownership_lines.append(ownership_tag.note.replace("Top-10 concentration ", "Top-10 concentration: "))
    while len(ownership_lines) < 3:
        if not any(line.startswith("Holders:") for line in ownership_lines):
            ownership_lines.append("Holders: —")
        elif not any(line.startswith("Smart money:") for line in ownership_lines):
            ownership_lines.append("Smart money: —")
        elif not any(line.startswith("Top-10 concentration:") for line in ownership_lines):
            ownership_lines.append("Top-10 concentration: —")
        else:
            break
    ownership_title = "💼 Ownership"
    parts.extend(["", ownership_title])
    parts.extend(_tree_lines(ownership_lines[:5]))

    market_lines = _note_lines(market_note)
    if market_lines:
        parts.extend(["", "📊 Market"])
        parts.extend(_tree_lines(market_lines))

    verdict_text = brief.quick_verdict or "Thin read. No conviction yet."
    parts.extend(["", f"🧠 Verdict {_dots(brief.signal_quality)}\n{verdict_text}"])
    risk_bits = [bit for bit in (_short_risk(risk) for risk in brief.top_risks[:2]) if bit] or ["Thin payload"]
    if "No signal match" in risk_bits and any("market-only read" in bit.lower() or "defensive market" in bit.lower() for bit in risk_bits):
        risk_bits = [bit for bit in risk_bits if bit != "No signal match"]
    risk_bits = list(dict.fromkeys(risk_bits))
    if "Runtime dependency missing" in risk_bits and "Live context limited" in risk_bits:
        risk_bits = [bit for bit in risk_bits if bit != "Live context limited"]
    parts.extend(["", f"⚠️ {' · '.join(risk_bits[:2])}"])
    return "\n".join(parts).strip() + "\n"


def _format_signal_card(brief: AnalysisBrief) -> str:
    symbol = brief.entity.replace("Signal:", "").strip()
    price_f, change_f, rank_i, _pair = _extract_price_tag(brief)
    gate = (brief.audit_gate or "").title()
    invalidation = _tag_note(brief, "Invalidation") or "Needs confirmation"
    entry_zone = _tag_note(brief, "Entry Zone")
    timing = _tag_note(brief, "Signal Timing")
    exit_pressure = _tag_note(brief, "Exit Pressure")
    strength_line = _strength_word(brief.signal_quality)
    if exit_pressure:
        exit_pct = exit_pressure.replace("Exit rate ", "").strip()
        strength_line = f"{strength_line} · {exit_pct} exited ⚠️" if exit_pct else strength_line

    audit_line = f"Audit: {'🔴' if gate.lower() == 'block' else '🟠' if gate.lower() == 'warn' else '🟢'} {gate}" if gate else "Audit: — not applicable"
    setup_lines = [audit_line]
    setup_lines.append(f"Entry zone: {entry_zone or '— limited'}")
    setup_lines.append(f"Strength: {strength_line}")
    setup_lines.append(f"Signal age: {_freshness_label(timing) if timing else '— limited'}")
    setup_lines.append(f"Invalidation: {_short_risk(invalidation)}")

    parts = [_signal_header(symbol, price_f, change_f, rank_i)]
    parts.extend(["", "⚡ Setup"])
    parts.extend(_tree_lines(setup_lines))

    context_lines = []
    for tag_name in ("Volume 24h", "Market Cap", "Max Gain", "Smart Money Inflow"):
        note = _tag_note(brief, tag_name)
        if note:
            context_lines.append(f"{tag_name}: {note}")
    if context_lines:
        parts.extend(["", "📊 Context"])
        parts.extend(_tree_lines(context_lines))

    evidence_lines = []
    spot_tag = _first_tag(brief, "Binance Spot")
    taker_tag = _first_tag(brief, "Taker Ratio")
    top_traders_tag = _first_tag(brief, "Top Traders")
    if spot_tag and spot_tag.note:
        evidence_lines.append(f"Spot: {spot_tag.note}")
    if taker_tag and taker_tag.note:
        evidence_lines.append(f"Taker flow: {taker_tag.note}")
    if top_traders_tag and top_traders_tag.note:
        evidence_lines.append(f"Top traders: {top_traders_tag.note}")
    if evidence_lines:
        parts.extend(["", "🧭 Evidence"])
        parts.extend(_tree_lines(evidence_lines[:4]))

    verdict_text = brief.quick_verdict or "Watchlist only. Needs confirmation."
    parts.extend(["", f"🧠 Verdict {_dots(brief.signal_quality)}\n{verdict_text}"])

    if brief.why_it_matters:
        parts.extend(["", "🔎 Read"])
        parts.extend(_tree_lines([brief.why_it_matters]))

    risk_bits = [
        bit for bit in (_short_risk(risk) for risk in brief.top_risks[:2])
        if bit and bit not in (brief.why_it_matters or "")
    ] or ["Thin payload"]
    if any("late setup" in (risk or "").lower() for risk in brief.top_risks[:2]) and "Most wallets already exited" not in risk_bits:
        risk_bits.insert(0, "Most wallets already exited")
    risk_bits = list(dict.fromkeys(risk_bits))
    if "Runtime dependency missing" in risk_bits and "Live context limited" in risk_bits:
        risk_bits = [bit for bit in risk_bits if bit != "Live context limited"]
    parts.extend(["", f"⚠️ {' · '.join(risk_bits[:2])}"])
    return "\n".join(parts).strip() + "\n"


def _format_wallet_card(brief: AnalysisBrief) -> str:
    follow_tag = next((tag for tag in brief.risk_tags if tag.name == "Follow Verdict"), None)
    follow = follow_tag.note if follow_tag and follow_tag.note else "Unknown"
    follow_emoji = "✅" if follow == "Track" else "⚠️" if follow == "Unknown" else "❌"
    address = brief.entity.replace("Wallet:", "").strip()
    short_address = address if len(address) <= 10 else f"{address[:6]}…{address[-5:]}"
    portfolio_value = ""
    marker = "This wallet tracks roughly $"
    if marker in (brief.why_it_matters or ""):
        portfolio_value = (brief.why_it_matters or "").split(marker, 1)[1].split(" ", 1)[0].rstrip(".")

    behavior_lines = []
    thin_wallet = any("thin" in (risk or "").lower() for risk in brief.top_risks[:2]) or "too thin" in (brief.quick_verdict or "").lower() or "unavailable" in (brief.quick_verdict or "").lower()
    watch = brief.what_to_watch_next[:3]
    lead_holding = _tag_note(brief, "Lead Holding")
    concentration = _tag_note(brief, "Concentration Risk")
    activity = _tag_note(brief, "Activity")
    style_profile = _tag_note(brief, "Style Profile")
    narrative = _tag_note(brief, "Narrative Risk")
    if thin_wallet:
        behavior_lines = ["Activity: Limited", "Top move: No rotation visible", "Drift: Follow signal unavailable"]
    elif style_profile or lead_holding or concentration or activity or narrative:
        behavior_lines = [
            f"Style: {style_profile or 'Mixed Observer'}",
            f"Activity: {activity or 'Visible'}",
            f"Lead holding: {lead_holding or 'Lead holding visible'}",
        ]
        if narrative:
            behavior_lines.append(f"Narrative: {narrative}")
        if concentration:
            behavior_lines.append(f"Drift: {concentration}")
    elif watch:
        labels = ["Activity", "Top move", "Drift"]
        for idx, item in enumerate(watch[:3]):
            cleaned = item.replace('whether ', '').replace('the wallet ', '').rstrip('.')
            behavior_lines.append(f"{labels[idx]}: {cleaned}")
    else:
        behavior_lines = ["Activity: Static", "Top move: No rotation visible", "Drift: No change detected"]

    header = f"👛 {short_address}"
    if portfolio_value:
        header += f" ~${portfolio_value}"
    header += f" {follow_emoji} {follow}"
    parts = [header]
    parts.extend(["", "⚡ Behavior"])
    parts.extend(_tree_lines(behavior_lines[:5]))
    holdings_lines = []
    if brief.beginner_note:
        for line in brief.beginner_note.splitlines():
            stripped = line.strip()
            if not stripped or stripped == "Public wallet posture" or stripped.startswith("24h Volatility:"):
                continue
            holdings_lines.append(stripped)
    if holdings_lines:
        parts.extend(["", "💼 Holdings"])
        parts.extend(_tree_lines(holdings_lines[:5]))
    dot_level = "Low" if follow == "Unknown" else "Medium" if follow == "Track" else "Low"
    verdict_text = brief.quick_verdict or "Limited read. Some structure visible."
    parts.extend(["", f"🧠 Verdict {_dots(dot_level)}\n{verdict_text}"])
    risk_bits = [bit for bit in (_short_risk(risk) for risk in brief.top_risks[:2]) if bit] or ["Thin payload"]
    risk_bits = ["Thin payload" if "thin" in bit.lower() or "wallet payload" in bit.lower() else bit for bit in risk_bits]
    risk_bits = list(dict.fromkeys(risk_bits))
    if "Runtime dependency missing" in risk_bits and "Live context limited" in risk_bits:
        risk_bits = [bit for bit in risk_bits if bit != "Live context limited"]
    if follow == "Unknown" and "not a follow signal" not in " ".join(risk_bits).lower():
        risk_bits.append("Not a follow signal")
    parts.extend(["", f"⚠️ {' · '.join(risk_bits[:2])}"])
    return "\n".join(parts).strip() + "\n"


def _runtime_banner(brief: AnalysisBrief) -> list[str]:
    trust_tag = next((tag for tag in brief.risk_tags if tag.name == "Live Trust"), None)
    if trust_tag:
        trust_line = trust_tag.level
        if brief.runtime_warning:
            trust_line += f" · {brief.runtime_warning}"
        elif trust_tag.note:
            trust_line += f" · generated {trust_tag.note}"
        return ["", f"🛰️ Live Trust\n{trust_line}"]
    if brief.runtime_state == "live_degraded" and brief.runtime_warning:
        return ["", f"🛰️ Live Trust\n🟡 Partial live / degraded · {brief.runtime_warning}"]
    if brief.runtime_state == "mock":
        return ["", "🛰️ Live Trust\n🔴 Mock / not live"]
    return []


def _format_watchtoday_card(brief: AnalysisBrief) -> str:
    parts = ["🌐 Watchtoday"]
    parts.extend(_runtime_banner(brief))

    signals_content = _section_content(brief, "smart money flow", "signal")
    attention_content = _section_content(brief, "trending now")
    rendered_sections = 0

    parts.extend(["", "⚡ Signals"])
    if signals_content.strip():
        parts.append(_treeify_block(signals_content))
    else:
        parts.append(_placeholder_tree("No clean board leader yet", "Signal breadth is limited"))
    rendered_sections += 1

    parts.extend(["", "🔥 Attention"])
    if attention_content.strip():
        parts.append(_treeify_block(attention_content))
    else:
        parts.append(_placeholder_tree("No strong attention pocket yet", "Attention is limited"))
    rendered_sections += 1

    extra_sections = [
        ("🏦 Exchange Board", _section_content(brief, "exchange board")),
        ("👀 Top 3 Picks", _section_content(brief, "top 3", "today")),
        ("🌊 Narrative", _section_content(brief, "narrative")),
        ("🚀 Meme Watch", _section_content(brief, "meme watch")),
        ("📈 Futures Sentiment", _section_content(brief, "futures")),
        ("🏆 Top Traders", _section_content(brief, "top trader")),
    ]
    for title, content in extra_sections:
        if rendered_sections >= 6:
            break
        if not content.strip():
            continue
        parts.extend(["", title])
        parts.append(_treeify_block(content))
        rendered_sections += 1

    board_verdict = brief.quick_verdict or "Quiet board. Hold posture."
    lower_board = board_verdict.lower()
    if "opportunity exists" in lower_board and "selectivity matters" in lower_board:
        board_verdict = "Moderate board. Be selective."
    elif "selective rather than defensive" in lower_board or "selectively instead of defensively" in lower_board:
        board_verdict = "Moderate board. Be selective."
    elif len(board_verdict) > 90:
        board_verdict = board_verdict.split(". ", 1)[0].rstrip(".") + "."
    parts.extend(["", f"🧠 Board {_dots(brief.signal_quality)}\n{board_verdict}"])
    risk_bits = [bit for bit in (_short_risk(risk) for risk in brief.top_risks[:2]) if bit] or ["Attention ≠ signal"]
    risk_bits = list(dict.fromkeys(risk_bits))
    if "Runtime dependency missing" in risk_bits and "Live context limited" in risk_bits:
        risk_bits = [bit for bit in risk_bits if bit != "Live context limited"]
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
    if attention_content.strip() and signals_content.strip():
        risk_bits.insert(0, "Attention ≠ signal")
    parts.extend(["", f"⚠️ {' · '.join(dict.fromkeys(risk_bits))}"])
    return "\n".join(parts).strip() + "\n"


def _format_alpha_card(brief: AnalysisBrief) -> str:
    parts = [_entity_line(brief.entity)]
    parts.extend(_runtime_banner(brief))

    market_content = _section_content(brief, "alpha market")
    context_content = _section_content(brief, "alpha context", "alpha snapshot")
    board_content = _section_content(brief, "alpha board")

    if market_content.strip():
        parts.extend(["", "📈 Alpha Market"])
        parts.append(_treeify_block(market_content))

    if context_content.strip():
        parts.extend(["", "🧭 Alpha Context"])
        parts.append(_treeify_block(context_content))

    if board_content.strip():
        parts.extend(["", "🗂️ Alpha Board"])
        parts.append(_treeify_block(board_content))

    verdict = brief.quick_verdict or "Alpha context is available but still thin."
    parts.extend(["", f"🧠 Verdict {_dots(brief.signal_quality)}\n{verdict}"])

    why = (brief.why_it_matters or "").strip()
    if why:
        parts.extend(["", "🔎 Read"])
        parts.extend(_tree_lines([why]))

    watch = [item for item in brief.what_to_watch_next[:3] if item and item.strip()]
    if watch:
        parts.extend(["", "👀 Watch"])
        parts.extend(_tree_lines(watch))

    risk_bits = [bit for bit in (_short_risk(risk) for risk in brief.top_risks[:2]) if bit]
    if not risk_bits:
        alpha_score = _first_tag(brief, "Alpha Score")
        alpha_id = _first_tag(brief, "Alpha ID")
        if alpha_score and alpha_score.note:
            risk_bits.append(f"Alpha score {alpha_score.note}")
        if alpha_id and alpha_id.note:
            risk_bits.append(alpha_id.note)
    if risk_bits:
        parts.extend(["", f"⚠️ {' · '.join(dict.fromkeys(risk_bits[:2]))}"])

    return "\n".join(parts).strip() + "\n"


def _format_futures_card(brief: AnalysisBrief) -> str:
    parts = [_entity_line(brief.entity)]
    parts.extend(_runtime_banner(brief))

    positioning_content = _section_content(brief, "futures positioning")
    evidence_content = _section_content(brief, "positioning evidence")

    if positioning_content.strip():
        parts.extend(["", "📊 Futures Positioning"])
        parts.append(_treeify_block(positioning_content))

    if evidence_content.strip():
        parts.extend(["", "🧭 Evidence"])
        parts.append(_treeify_block(evidence_content))

    crowding_tag = _first_tag(brief, "Crowding")
    squeeze_tag = _first_tag(brief, "Squeeze Risk")
    analytics_lines = []
    if crowding_tag and crowding_tag.note:
        analytics_lines.append(f"Crowding: {crowding_tag.note}")
    if squeeze_tag and squeeze_tag.note:
        analytics_lines.append(f"Squeeze risk: {squeeze_tag.note}")
    if analytics_lines:
        parts.extend(["", "🧪 Positioning Read"])
        parts.extend(_tree_lines(analytics_lines))

    verdict = brief.quick_verdict or "Futures context is available but still thin."
    parts.extend(["", f"🧠 Verdict {_dots(brief.signal_quality)}\n{verdict}"])

    why = (brief.why_it_matters or "").strip()
    if why:
        parts.extend(["", "🔎 Read"])
        parts.extend(_tree_lines([why]))

    watch = [item for item in brief.what_to_watch_next[:3] if item and item.strip()]
    if watch:
        parts.extend(["", "👀 Watch"])
        parts.extend(_tree_lines(watch))

    risk_bits = [bit for bit in (_short_risk(risk) for risk in brief.top_risks[:2]) if bit]
    if risk_bits:
        parts.extend(["", f"⚠️ {' · '.join(dict.fromkeys(risk_bits[:2]))}"])

    return "\n".join(parts).strip() + "\n"


def _format_portfolio_card(brief: AnalysisBrief) -> str:
    total_value = ""
    why = brief.why_it_matters or ""
    marker = "Estimated visible Spot value is about $"
    if marker in why:
        total_value = why.split(marker, 1)[1].split(" ", 1)[0].rstrip(".")

    dust_state = "dust" in (brief.quick_verdict or "").lower() or any(tag.name == "Dust State" for tag in brief.risk_tags)
    stable_tag = next((tag for tag in brief.risk_tags if tag.name == "Stablecoin Share" and tag.note), None)
    lead_group_tag = _first_tag(brief, "Lead Group")
    margin_tag = _first_tag(brief, "Margin Exposure")
    short_trend_tag = _first_tag(brief, "Short Trend")
    coverage_tag = _first_tag(brief, "Coverage")
    style_tag = _first_tag(brief, "Style Profile")
    top3_tag = _first_tag(brief, "Top 3")
    effective_tag = _first_tag(brief, "Effective Positions")
    alpha_tag = _first_tag(brief, "Alpha Exposure")
    top_lines = brief.beginner_note.splitlines()[:5] if brief.beginner_note else []
    top_asset = top_lines[0].split("~", 1)[0].replace("Dust balance —", "").strip() if top_lines else "—"
    posture = brief.signal_quality or "Defensive"
    risk_pct = "—"
    if "risk assets are " in why:
        try:
            risk_pct = why.split("risk assets are ", 1)[1].split("%", 1)[0] + "%"
        except Exception:
            pass

    unavailable = "unavailable" in (brief.quick_verdict or "").lower()
    parts = [f"📂 Holdings Binance Spot {'~$' + total_value if total_value else ''}".rstrip()]
    parts.extend(["", "⚡ Posture"])
    if unavailable:
        posture_lines = ["Stables: —", "Risk: —", "Top asset: —"]
    elif dust_state:
        posture_lines = ["Stables: dust-only 💵", "Risk: near-zero", f"Top asset: {top_asset or '—'}"]
    else:
        posture_lines = [
            f"Stables: {stable_tag.note} 💵" if stable_tag else "Stables: —",
            f"Risk: {risk_pct}",
            f"Top asset: {top_asset}",
        ]
        if lead_group_tag and lead_group_tag.note:
            posture_lines.append(f"Lead group: {lead_group_tag.note}")
    parts.extend(_tree_lines(posture_lines))

    parts.extend(["", "💼 Top Holdings"])
    if top_lines:
        parts.extend(_tree_lines(top_lines[:5]))
    else:
        parts.extend(_tree_lines(["No priced holdings visible", "Read-only snapshot unavailable"] if unavailable else ["No priced holdings visible", "Waiting for fuller snapshot"]))

    analytics_lines = []
    if style_tag and style_tag.note:
        analytics_lines.append(f"Style: {style_tag.note}")
    if top3_tag and top3_tag.note:
        analytics_lines.append(f"Top 3: {top3_tag.note}")
    if effective_tag and effective_tag.note:
        analytics_lines.append(f"Effective positions: {effective_tag.note}")
    if alpha_tag and alpha_tag.note:
        analytics_lines.append(f"Alpha exposure: {alpha_tag.note}")
    if coverage_tag and coverage_tag.note:
        analytics_lines.append(f"Coverage: {coverage_tag.note}")
    if analytics_lines:
        parts.extend(["", "🧪 Analytics"])
        parts.extend(_tree_lines(analytics_lines[:4]))

    if margin_tag and margin_tag.note:
        parts.extend(["", "🏦 Margin"])
        parts.extend(_tree_lines(_note_lines(margin_tag.note)))

    if short_trend_tag and short_trend_tag.note:
        parts.extend(["", "📈 Snapshot Trend"])
        parts.extend(_tree_lines([short_trend_tag.note]))

    verdict_text = brief.quick_verdict or "Portfolio read is unavailable right now."
    parts.extend(["", f"🧠 Verdict {_dots(posture)}\n{verdict_text}"])
    freshness = next((tag.note for tag in brief.risk_tags if tag.name == "Freshness" and tag.note), "")
    footer_bits = [f"Snapshot {freshness}" if freshness else "Read-only estimate", "Read-only estimate"]
    if unavailable:
        risk_bits = [bit for bit in (_short_risk(risk) for risk in brief.top_risks[:2]) if bit] or ["Read-only estimate"]
        footer_bits = list(dict.fromkeys(risk_bits + footer_bits))[:2]
    else:
        footer_bits = list(dict.fromkeys(footer_bits))[:2]
    parts.extend(["", f"⚠️ {' · '.join(footer_bits)}"])
    return "\n".join(parts).strip() + "\n"


def format_brief(brief: AnalysisBrief) -> str:
    if brief.entity.startswith("Price:"):
        rendered = _format_price_card(brief)
    elif brief.entity.startswith("Brief:"):
        rendered = _format_compact_brief_card(brief)
    elif brief.entity.startswith("Risk:"):
        rendered = _format_risk_card(brief)
    elif brief.entity.startswith("Audit:"):
        rendered = _format_audit_card(brief)
    elif brief.entity.startswith("Meme:"):
        rendered = _format_token_card(brief)
    elif brief.entity.startswith("Token:"):
        rendered = _format_token_card(brief)
    elif brief.entity.startswith("Signal:"):
        rendered = _format_signal_card(brief)
    elif brief.entity.startswith("Wallet:"):
        rendered = _format_wallet_card(brief)
    elif brief.entity.startswith("Portfolio:"):
        rendered = _format_portfolio_card(brief)
    elif brief.entity == "Market Watch":
        rendered = _format_watchtoday_card(brief)
    elif brief.entity == "Binance Alpha" or brief.entity.startswith("Alpha ·"):
        rendered = _format_alpha_card(brief)
    elif brief.entity.startswith("Futures ·"):
        rendered = _format_futures_card(brief)
    else:
        parts = [_entity_line(brief.entity), "", brief.quick_verdict]
        rendered = "\n".join(parts).strip() + "\n"

    banner = _runtime_banner(brief)
    if not banner or "🛰️ Live Trust" in rendered:
        return rendered

    lines = rendered.strip().splitlines()
    if not lines:
        return rendered
    rebuilt = [lines[0], *banner, *lines[1:]]
    return "\n".join(rebuilt).strip() + "\n"
