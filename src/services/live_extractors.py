from __future__ import annotations

import re
from typing import Any


def extract_token_context(raw: dict[str, Any], symbol: str) -> dict[str, Any]:
    token_info = raw.get("query-token-info", {})
    market_rank = raw.get("crypto-market-rank", {})
    signal = raw.get("trading-signal", {})
    audit = raw.get("query-token-audit", {})

    metadata = token_info.get("metadata", {})
    search_item = _best_token_match(token_info.get("search"), symbol, metadata) or metadata or token_info
    dynamic = token_info.get("dynamic", {})
    resolved_symbol = str(search_item.get("symbol") or metadata.get("symbol") or symbol)
    audit_payload = audit.get("data", audit)
    audit_flags, audit_risks = _extract_audit_flags_and_risks(audit_payload)
    market_risks = _extract_market_rank_risks(market_rank, resolved_symbol)
    signal_risks = _extract_signal_risks(signal)
    first_signal = _first_item(signal.get("data")) or signal
    signal_age_hours = _signal_age_hours(first_signal)
    signal_freshness = _signal_freshness(signal_age_hours)
    audit_gate, blocked_reason = _audit_gate_state(audit_payload, audit_flags)

    resolved_signal_status = signal.get("status") or signal.get("direction") or ("watch" if _first_item(signal.get("data")) else "unmatched")
    top_holder_concentration_pct = _pick_number(_best_symbol_match((market_rank.get("data", {}).get("tokens", []) or market_rank.get("tokens", []) or []), _normalize_match_key(resolved_symbol)) or {}, "holdersTop10Percent", "top10HoldersPercentage")

    return {
        "symbol": resolved_symbol,
        "display_name": search_item.get("name") or metadata.get("name") or search_item.get("symbol") or symbol,
        "price": _pick_number(dynamic, "price") or _pick_number(search_item, "price"),
        "liquidity": _pick_number(dynamic, "liquidity") or _pick_number(search_item, "liquidity"),
        "holders": _pick_int(dynamic, "holders", "kycHolderCount") or _pick_int(search_item, "holders"),
        "top_holder_concentration_pct": top_holder_concentration_pct,
        "market_rank_context": _build_market_rank_context(market_rank, resolved_symbol),
        "signal_status": resolved_signal_status,
        "signal_trigger_context": _build_signal_context(signal),
        "audit_flags": audit_flags,
        "major_risks": _merge_risks(signal_risks, audit_risks, market_risks),
        "smart_money_count": _pick_int(first_signal, "smartMoneyCount"),
        "exit_rate": _pick_number(first_signal, "exitRate", "exit_rate"),
        "signal_age_hours": signal_age_hours,
        "signal_freshness": signal_freshness,
        "audit_gate": audit_gate,
        "blocked_reason": blocked_reason,
    }


def extract_wallet_context(raw: dict[str, Any], address: str) -> dict[str, Any]:
    address_info = raw.get("query-address-info", {})
    items = address_info.get("list") or address_info.get("data", {}).get("list") or []

    if not items and (address_info.get("top_holdings") or address_info.get("portfolio_value") is not None):
        holdings_count = _to_int(address_info.get("holdings_count"))
        portfolio_value = _to_float(address_info.get("portfolio_value"))
        top_holdings = address_info.get("top_holdings", [])
        top_concentration_pct = _to_float(address_info.get("top_concentration_pct"))
        change_24h = _to_float(address_info.get("change_24h"))
        major_risks = [str(x) for x in address_info.get("major_risks", [])]
        if holdings_count <= 0 and top_holdings:
            holdings_count = len(top_holdings)
        if not major_risks and not top_holdings and portfolio_value <= 0:
            major_risks = ["Thin payload."]
        return {
            "address": address,
            "portfolio_value": portfolio_value,
            "holdings_count": holdings_count,
            "top_holdings": top_holdings,
            "top_concentration_pct": top_concentration_pct,
            "change_24h": change_24h,
            "notable_exposures": [str(x) for x in address_info.get("notable_exposures", [])],
            "major_risks": major_risks,
            "style_profile": str(address_info.get("style_profile", "")),
            "exposure_breakdown": [str(x) for x in address_info.get("exposure_breakdown", [])],
        }

    holdings = []
    portfolio_value = 0.0
    biggest = 0.0
    exposure_weights: dict[str, float] = {}
    symbol_weights: list[tuple[str, float]] = []
    for item in items:
        symbol = str(item.get("symbol", "UNKNOWN"))
        price = _to_float(item.get("price"))
        qty = _to_float(item.get("remainQty"))
        value = price * qty
        portfolio_value += value
        biggest = max(biggest, value)
        change_24h = _to_float(item.get("percentChange24h"))
        holdings.append({"symbol": symbol, "value": value, "change_24h": change_24h})
        symbol_weights.append((symbol, value))
        bucket = _wallet_exposure_bucket(symbol)
        exposure_weights[bucket] = exposure_weights.get(bucket, 0.0) + value

    top_holdings = []
    if portfolio_value > 0:
        holdings.sort(key=lambda x: x["value"], reverse=True)
        for item in holdings[:5]:
            top_holdings.append({"symbol": item["symbol"], "weight_pct": (item["value"] / portfolio_value) * 100})

    change_24h = 0.0
    if portfolio_value > 0:
        weighted = 0.0
        for item in holdings:
            weighted += item["value"] * item["change_24h"]
        change_24h = weighted / portfolio_value

    top_concentration_pct = (biggest / portfolio_value) * 100 if portfolio_value > 0 else 0.0
    notable_exposures = [name for name, value in sorted(exposure_weights.items(), key=lambda pair: pair[1], reverse=True) if value > 0][:5]
    exposure_breakdown = []
    if portfolio_value > 0:
        for name, value in sorted(exposure_weights.items(), key=lambda pair: pair[1], reverse=True)[:4]:
            exposure_breakdown.append(f"{name} {(value / portfolio_value) * 100:.1f}%")

    risks: list[str] = []
    if top_concentration_pct >= 60:
        risks.append("Wallet is highly concentrated in one token or theme.")
    if portfolio_value > 0 and len(exposure_weights) <= 1 and len(items) >= 3:
        risks.append("Wallet diversification is weaker than the holding count first suggests because exposures cluster into one theme.")

    style_profile = _wallet_style_profile(top_concentration_pct, len(items), exposure_weights, change_24h)
    style_bits: list[str] = []
    if notable_exposures:
        style_bits.append(f"Narrative bias: {', '.join(notable_exposures[:2])}")
    if style_profile:
        style_bits.append(f"Style profile: {style_profile}")
    if top_concentration_pct >= 75:
        style_bits.append("Risk posture: concentrated")
    elif len(items) >= 5 and len(exposure_weights) >= 2:
        style_bits.append("Risk posture: diversified")
    else:
        style_bits.append("Risk posture: mixed")
    style_read = " | ".join(style_bits)

    if portfolio_value >= 100_000 and top_concentration_pct < 70 and len(items) >= 5 and len(exposure_weights) >= 2:
        follow_verdict = "Track"
    elif portfolio_value > 0 or len(items) > 0:
        follow_verdict = "Unknown"
    else:
        follow_verdict = "Don't follow"

    return {
        "address": address,
        "portfolio_value": portfolio_value,
        "holdings_count": len(items),
        "top_holdings": top_holdings,
        "top_concentration_pct": top_concentration_pct,
        "change_24h": change_24h,
        "notable_exposures": notable_exposures[:5],
        "major_risks": risks,
        "follow_verdict": follow_verdict,
        "style_read": style_read,
        "style_profile": style_profile,
        "exposure_breakdown": exposure_breakdown,
    }


def extract_watch_today_context(raw: dict[str, Any]) -> dict[str, Any]:
    market_rank = raw.get("crypto-market-rank", {})
    meme_rush = raw.get("meme-rush", {})
    signal = raw.get("trading-signal", {})

    top_narratives = _extract_top_narratives(market_rank, meme_rush)
    strongest_signals = _extract_strongest_signals(signal)
    risk_zones = _extract_risk_zones(market_rank, meme_rush)
    trending_now = _extract_trending_now(market_rank)
    smart_money_flow = _extract_smart_money_flow(market_rank, signal)
    social_hype = _extract_social_hype(market_rank)
    meme_watch = _extract_meme_watch(meme_rush)
    exchange_board = _extract_watchtoday_exchange_board(market_rank)

    if not strongest_signals and exchange_board:
        strongest_signals = [f"{exchange_board[0]} — exchange-led momentum read"]
    if not trending_now and exchange_board:
        trending_now = exchange_board[:2]
    if not smart_money_flow and strongest_signals:
        smart_money_flow = strongest_signals[:3]
    if not social_hype:
        if trending_now:
            social_hype = trending_now[:2]
        elif top_narratives:
            social_hype = [f"{item} — narrative attention visible" for item in top_narratives[:2]]
    if not meme_watch and top_narratives:
        meme_watch = [f"{item} — narrative/meme crossover watch" for item in top_narratives[:2] if any(x in item.lower() for x in ["meme", "dog", "frog", "community", "ai"])]
    top_picks = _extract_top_picks(trending_now, strongest_signals, top_narratives, exchange_board)
    if not top_picks:
        top_picks = _extract_top_picks(trending_now, strongest_signals, top_narratives, exchange_board)

    return {
        "top_narratives": top_narratives,
        "strongest_signals": strongest_signals,
        "risk_zones": risk_zones,
        "market_takeaway": _build_market_rank_context(market_rank) or _extract_topic_summary(meme_rush),
        "major_risks": _merge_risks(_extract_market_rank_risks(market_rank), _extract_meme_risks(meme_rush), _extract_signal_risks(signal)),
        "trending_now": trending_now,
        "smart_money_flow": smart_money_flow,
        "social_hype": social_hype,
        "meme_watch": meme_watch,
        "top_picks": top_picks,
        "exchange_board": exchange_board,
    }


def extract_signal_context(raw: dict[str, Any], token: str) -> dict[str, Any]:
    signal = raw.get("trading-signal", {})
    first_signal = _first_item(signal.get("data")) or signal
    audit = raw.get("query-token-audit", {})
    audit_payload = audit.get("data", audit)
    audit_flags, audit_risks = _extract_audit_flags_and_risks(audit_payload)

    direction = str(first_signal.get("direction", "")).lower()
    status = first_signal.get("status") or ("bullish" if direction == "buy" else "bearish" if direction == "sell" else "unknown")
    if first_signal == signal and not signal.get("data"):
        status = "unmatched"
    supporting_context = _build_signal_context(signal)
    signal_age_hours = _signal_age_hours(first_signal)
    signal_freshness = _signal_freshness(signal_age_hours)
    audit_gate, blocked_reason = _audit_gate_state(audit_payload, audit_flags)

    return {
        "token": first_signal.get("ticker") or token,
        "signal_status": status,
        "trigger_price": _pick_number(first_signal, "alertPrice", "trigger_price"),
        "current_price": _pick_number(first_signal, "currentPrice", "current_price"),
        "max_gain": _pick_number(first_signal, "maxGain", "max_gain"),
        "exit_rate": _pick_number(first_signal, "exitRate", "exit_rate"),
        "audit_flags": audit_flags,
        "supporting_context": supporting_context,
        "major_risks": _merge_risks(_extract_signal_risks(signal), audit_risks),
        "smart_money_count": _pick_int(first_signal, "smartMoneyCount"),
        "signal_age_hours": signal_age_hours,
        "signal_freshness": signal_freshness,
        "audit_gate": audit_gate,
        "blocked_reason": blocked_reason,
    }


def extract_audit_context(raw: dict[str, Any], symbol: str) -> dict[str, Any]:
    token_info = raw.get("query-token-info", {})
    audit = raw.get("query-token-audit", {})
    audit_payload = audit.get("data", audit)
    metadata = token_info.get("metadata", {})
    search_item = _best_token_match(token_info.get("search"), symbol, metadata) or metadata or token_info
    display_symbol = str(search_item.get("symbol") or metadata.get("symbol") or symbol)
    display_name = str(search_item.get("name") or metadata.get("name") or display_symbol)
    audit_flags, audit_risks = _extract_audit_flags_and_risks(audit_payload)
    audit_gate, blocked_reason = _audit_gate_state(audit_payload, audit_flags)
    extra = audit_payload.get("extraInfo") or {}
    buy_tax = _to_float(extra.get("buyTax"))
    sell_tax = _to_float(extra.get("sellTax"))
    risk_level = str(audit_payload.get("riskLevelEnum") or ("HIGH" if audit_gate == "BLOCK" else "MEDIUM" if audit_gate == "WARN" else "LOW")).title()
    summary_bits: list[str] = []
    if audit_payload.get("hasResult") and audit_payload.get("isSupported"):
        summary_bits.append(f"Risk level {audit_payload.get('riskLevel', 0)} ({risk_level.upper()})")
    if buy_tax > 0 or sell_tax > 0:
        summary_bits.append(f"Buy tax {buy_tax:.2f}% | Sell tax {sell_tax:.2f}%")
    if not summary_bits:
        summary_bits.append(blocked_reason or "Audit output is limited right now.")

    return {
        "symbol": display_symbol,
        "display_name": display_name,
        "audit_gate": audit_gate,
        "blocked_reason": blocked_reason,
        "audit_flags": audit_flags,
        "major_risks": _merge_risks(audit_risks),
        "risk_level": risk_level,
        "audit_summary": "; ".join(summary_bits),
    }


def extract_meme_context(raw: dict[str, Any], symbol: str) -> dict[str, Any]:
    token = extract_token_context(raw, symbol)
    token_info = raw.get("query-token-info", {})
    market_rank = raw.get("crypto-market-rank", {})
    signal = raw.get("trading-signal", {})
    meme_rush = raw.get("meme-rush", {})
    first_signal = _first_item(signal.get("data")) or {}
    metadata = token_info.get("metadata", {}) or {}
    search_item = _best_token_match(token_info.get("search"), symbol, metadata) or metadata or {}
    market_tokens = market_rank.get("data", {}).get("tokens", []) or market_rank.get("tokens", []) or []
    matched_rank = _best_symbol_match(market_tokens, _normalize_match_key(token.get("symbol", symbol))) if market_tokens else None
    meme_items = meme_rush.get("data", []) or meme_rush.get("tokens", []) or []
    matched_meme = _best_symbol_match(meme_items, _normalize_match_key(token.get("symbol", symbol))) if meme_items else None

    launch_platform = str(first_signal.get("launchPlatform") or search_item.get("launchPlatform") or metadata.get("launchPlatform") or "")
    is_alpha = bool(first_signal.get("isAlpha"))
    status = str(first_signal.get("status") or "").lower()
    exit_rate = _pick_number(first_signal, "exitRate", "exit_rate")
    progress = _pick_number(first_signal, "progress")
    top_holder_concentration_pct = _pick_number(matched_rank or {}, "holdersTop10Percent", "top10HoldersPercentage") or _pick_number(matched_meme or {}, "holdersTop10Percent")
    social_brief = ""
    if matched_rank:
        social_info = matched_rank.get("socialHypeInfo") or {}
        social_brief = str(social_info.get("socialSummaryBriefTranslated") or social_info.get("socialSummaryBrief") or "")
    meme_score = _pick_number(matched_meme or {}, "topicHeatScore", "score")

    tag_values = []
    for source in (search_item.get("tokenTag") or {}, metadata.get("tokenTag") or {}):
        if isinstance(source, dict):
            tag_values.extend([str(k).lower() for k in source.keys()])
    market_context = str(token.get("market_rank_context", "")).lower()
    symbol_upper = str(token.get("symbol", symbol)).upper()
    display_name = str(token.get("display_name", symbol))

    meme_like = any(x in market_context for x in ["meme", "community"]) or any(x in " ".join(tag_values) for x in ["meme", "community", "dog", "frog"])
    if social_brief and any(x in social_brief.lower() for x in ["meme", "community", "viral", "trend"]):
        meme_like = True
    known_meme_symbols = {"DOGE", "SHIB", "PEPE", "BONK", "FLOKI", "WIF"}
    if symbol_upper in known_meme_symbols:
        meme_like = True

    lifecycle = "unknown"
    if progress >= 90:
        lifecycle = "finalizing"
    elif status in {"timeout", "exitrate", "exited"} or exit_rate >= 70:
        lifecycle = "late"
    elif status in {"valid", "watch", "bullish", "triggered"} or token.get("smart_money_count", 0) > 0:
        lifecycle = "active"
    elif meme_like or meme_score > 0:
        lifecycle = "attention"

    risks = list(token.get("major_risks", []))
    if top_holder_concentration_pct >= 85:
        risks.append(f"Top-holder concentration is extreme at {top_holder_concentration_pct:.1f}%.")
    elif top_holder_concentration_pct >= 70:
        risks.append(f"Top-holder concentration is high at {top_holder_concentration_pct:.1f}%.")
    if not meme_like:
        risks.insert(0, "This asset does not currently read as a clear meme candidate from the available live context.")

    return {
        "symbol": token.get("symbol", symbol),
        "display_name": display_name,
        "price": token.get("price", 0.0),
        "liquidity": token.get("liquidity", 0.0),
        "market_rank_context": token.get("market_rank_context", ""),
        "signal_status": token.get("signal_status", "unknown"),
        "audit_flags": token.get("audit_flags", []),
        "major_risks": _unique(risks),
        "smart_money_count": token.get("smart_money_count", 0),
        "exit_rate": token.get("exit_rate", 0.0),
        "signal_age_hours": token.get("signal_age_hours", 0.0),
        "signal_freshness": token.get("signal_freshness", "UNKNOWN"),
        "audit_gate": token.get("audit_gate", "ALLOW"),
        "blocked_reason": token.get("blocked_reason", ""),
        "launch_platform": launch_platform,
        "is_alpha": is_alpha,
        "lifecycle_stage": lifecycle,
        "bonded_progress": progress,
        "meme_score": meme_score,
        "social_brief": social_brief,
        "top_holder_concentration_pct": top_holder_concentration_pct,
    }


def _extract_audit_flags_and_risks(audit: dict[str, Any]) -> tuple[list[str], list[str]]:
    if not audit:
        return [], []

    if "flags" in audit or "risks" in audit:
        return _unique([str(x) for x in audit.get("flags", [])]), _unique([str(x) for x in audit.get("risks", [])])

    if not audit.get("hasResult") or not audit.get("isSupported"):
        return [], []

    flags: list[str] = []
    risks: list[str] = []
    level = _to_int(audit.get("riskLevel"))
    suppress_unverified_only = bool(audit.get("isHidden")) and level == 0 and not (audit.get("extraInfo") or {}).get("isVerified", False)
    if level >= 4:
        flags.append(f"Risk level {level} ({audit.get('riskLevelEnum', 'HIGH')})")
    elif level >= 2:
        flags.append(f"Risk level {level} ({audit.get('riskLevelEnum', 'MEDIUM')})")

    buy_tax = _to_float((audit.get("extraInfo") or {}).get("buyTax"))
    sell_tax = _to_float((audit.get("extraInfo") or {}).get("sellTax"))
    for label, value in (("Buy tax", buy_tax), ("Sell tax", sell_tax)):
        if value > 10:
            flags.append(f"{label} above 10%")
        elif value >= 5:
            risks.append(f"{label} is elevated at {value:.2f}%.")

    for item in audit.get("riskItems", []) or []:
        category = item.get("name") or item.get("id") or "Risk"
        for detail in item.get("details", []) or []:
            if detail.get("isHit"):
                title = detail.get("title") or "Risk detected"
                desc = detail.get("description") or ""
                if suppress_unverified_only and title == "Contract Code Not Verified":
                    continue
                flags.append(title)
                risks.append(f"{category}: {title}. {desc}".strip())
    return _unique(flags), _unique(risks)


def _extract_market_rank_risks(market_rank: dict[str, Any], symbol: str | None = None) -> list[str]:
    risks = list(market_rank.get("risks", []) or [])
    tokens = market_rank.get("data", {}).get("tokens", []) or market_rank.get("tokens", []) or []
    if symbol is None:
        for token in tokens[:5]:
            top10 = _pick_number(token, "holdersTop10Percent", "top10HoldersPercentage")
            if top10 >= 90:
                risks.append(f"{token.get('symbol', 'Token')} has extreme top-10 holder concentration.")
            elif top10 >= 80:
                risks.append(f"{token.get('symbol', 'Token')} has very high top-10 holder concentration.")
            audit_info = token.get("auditInfo") or {}
            risk_num = _to_int(audit_info.get("riskNum"))
            caution_num = _to_int(audit_info.get("cautionNum"))
            if risk_num > 0 or caution_num > 0:
                risks.append(f"{token.get('symbol', 'Token')} shows audit cautions in market rank context.")
        return _unique(risks)

    target = _normalize_match_key(symbol)
    token = _best_symbol_match(tokens, target) if target else None
    if not token:
        return _unique(risks)

    top10 = _pick_number(token, "holdersTop10Percent", "top10HoldersPercentage")
    if top10 >= 80:
        risks.append(f"{token.get('symbol', 'Token')} has very high top-10 holder concentration.")
    audit_info = token.get("auditInfo") or {}
    risk_num = _to_int(audit_info.get("riskNum"))
    caution_num = _to_int(audit_info.get("cautionNum"))
    if risk_num > 0 or caution_num > 0:
        risks.append(f"{token.get('symbol', 'Token')} shows audit cautions in market rank context.")
    return _unique(risks)


def _extract_signal_risks(signal: dict[str, Any]) -> list[str]:
    risks = list(signal.get("risks", []) or [])
    first = _first_item(signal.get("data")) or signal
    exit_rate = _pick_number(first, "exitRate", "exit_rate")
    status = str(first.get("status", ""))
    age_hours = _signal_age_hours(first)
    if status == "timeout":
        risks.append("Signal timed out and may no longer be actionable.")
    if exit_rate >= 70:
        risks.append("Smart money exit rate is high, which may indicate the move is aging.")
    elif exit_rate >= 40:
        risks.append("Smart money exit rate is already mixed, so follow-through may be less clean.")
    if age_hours >= 8:
        risks.append("Signal is stale enough that timing quality may already be degraded.")
    elif age_hours >= 2:
        risks.append("Signal is aging and needs fresher confirmation.")
    return _unique(risks)


def _extract_meme_risks(meme_rush: dict[str, Any]) -> list[str]:
    risks = list(meme_rush.get("risks", []) or [])
    items = meme_rush.get("data", []) or meme_rush.get("tokens", []) or []
    for item in items[:5]:
        if _to_int(item.get("tagDevWashTrading")) == 1:
            risks.append(f"{item.get('symbol', 'Token')} shows dev wash-trading risk.")
        if _to_int(item.get("tagInsiderWashTrading")) == 1:
            risks.append(f"{item.get('symbol', 'Token')} shows insider wash-trading risk.")
        if _pick_number(item, "holdersTop10Percent") >= 80:
            risks.append(f"{item.get('symbol', 'Token')} has concentrated top-10 holders.")
    return _unique(risks)


def _build_market_rank_context(market_rank: dict[str, Any], symbol: str | None = None) -> str:
    tokens = market_rank.get("data", {}).get("tokens", []) or market_rank.get("tokens", []) or []
    if symbol is None:
        if not tokens:
            return ""
        leaders = [str(item.get("symbol") or "Token") for item in tokens[:3]]
        return f"Current rank leaders: {', '.join(leaders)}. Opportunity exists, but selectivity matters."

    target = _normalize_match_key(symbol)
    matched = _best_symbol_match(tokens, target) if target else None
    if matched:
        matched_symbol = matched.get("symbol", symbol or "This token")
        return f"{matched_symbol} appears in current market-rank screens with visible liquidity and activity context."

    return ""


def _build_signal_context(signal: dict[str, Any]) -> str:
    first = _first_item(signal.get("data"))
    if not first:
        summary = str(signal.get("summary") or "").strip()
        if summary:
            return summary
        return "No matched smart-money signal is visible for this token in the current live board."

    ticker = first.get("ticker", "This token")
    direction = str(first.get("direction", "")).lower()
    platform = first.get("launchPlatform") or ""
    count = _to_int(first.get("smartMoneyCount"))
    status = first.get("status") or "unknown"
    freshness = _signal_freshness(_signal_age_hours(first))
    parts = [f"{ticker} has a {direction or 'smart-money'} signal"]
    if count:
        parts.append(f"from {count} smart-money addresses")
    if platform:
        parts.append(f"on {platform}")
    parts.append(f"with status {status}")
    if freshness != "UNKNOWN":
        parts.append(f"and {freshness.lower()} timing")
    return " ".join(parts).strip() + "."


WALLET_EXPOSURE_BUCKETS = {
    "meme": {"DOGE", "SHIB", "PEPE", "BONK", "FLOKI", "WIF"},
    "ai": {"AI", "FET", "AGIX", "OCEAN", "TAO", "ARKM"},
    "l1": {"BTC", "ETH", "BNB", "SOL", "AVAX", "SUI", "APT"},
    "defi": {"UNI", "AAVE", "MKR", "SNX", "CRV", "COMP"},
    "infra": {"LINK", "ATOM", "OP", "ARB", "TIA", "PYTH"},
}


def _wallet_exposure_bucket(symbol: str) -> str:
    upper = str(symbol or "").upper()
    for bucket, symbols in WALLET_EXPOSURE_BUCKETS.items():
        if upper in symbols:
            return bucket.upper()
    return upper



def _wallet_style_profile(top_concentration_pct: float, holdings_count: int, exposure_weights: dict[str, float], change_24h: float) -> str:
    if top_concentration_pct >= 75:
        base = "high-conviction concentrated"
    elif holdings_count >= 8 and len(exposure_weights) >= 3:
        base = "multi-theme diversified"
    elif holdings_count >= 5:
        base = "selective diversified"
    else:
        base = "narrow watchlist"

    if change_24h >= 8:
        return base + " momentum-seeking"
    if change_24h <= -8:
        return base + " under pressure"
    return base



def _extract_watchtoday_exchange_board(market_rank: dict[str, Any]) -> list[str]:
    rows: list[str] = []
    tokens = market_rank.get("data", {}).get("tokens", []) or market_rank.get("tokens", []) or []
    for item in tokens[:5]:
        symbol = item.get("symbol") or "Token"
        change = _pick_number(item, "priceChangePercent24h", "priceChange24h", "change24h", "percentChange24h")
        liq = _pick_number(item, "liquidity", "liquidityUsd")
        if change or liq:
            bits = [f"{symbol} {change:+.1f}%" if change else str(symbol)]
            if liq > 0:
                bits.append(f"liq ${liq/1_000_000:.1f}M")
            rows.append(" | ".join(bits))
    return _unique(rows)[:3]


def _extract_top_narratives(market_rank: dict[str, Any], meme_rush: dict[str, Any]) -> list[str]:
    direct_market = [str(x) for x in market_rank.get("top_narratives", []) or []]
    if direct_market:
        return direct_market

    out: list[str] = []
    tokens = market_rank.get("data", {}).get("tokens", []) or market_rank.get("tokens", []) or []
    for item in tokens[:8]:
        for label in (item.get("tokenTag") or {}).keys():
            out.append(str(label))
    leaderboard = market_rank.get("data", {}).get("leaderBoardList", []) or market_rank.get("leaderBoardList", []) or []
    for item in leaderboard[:3]:
        brief = item.get("socialHypeInfo", {}).get("socialSummaryBriefTranslated") or item.get("socialHypeInfo", {}).get("socialSummaryBrief")
        if brief:
            out.append(brief)
    topics = meme_rush.get("data", []) or []
    for topic in topics[:3]:
        name = topic.get("name", {}).get("topicNameEn") or topic.get("name", {}).get("topicNameCn") or topic.get("type")
        if name:
            out.append(str(name))
    out.extend([str(x) for x in meme_rush.get("top_narratives", []) or []])
    cleaned = []
    for item in out:
        short = str(item).strip()
        if short and len(short) <= 40:
            cleaned.append(short)
    return _unique(cleaned)[:5]


def _extract_topic_summary(meme_rush: dict[str, Any]) -> str:
    topics = meme_rush.get("data", []) or []
    if topics:
        top = topics[0]
        name = top.get("name", {}).get("topicNameEn") or top.get("type") or "topic"
        inflow = top.get("topicNetInflow") or top.get("topicNetInflowAth")
        if inflow:
            return f"{name} is a leading topic with visible net inflow of {inflow}."
        return f"{name} is a leading topic in current topic-rush context."
    return ""


def _signal_age_hours(signal_item: dict[str, Any]) -> float:
    raw = signal_item.get("timeFrame") or signal_item.get("timeframe") or signal_item.get("signalAgeMs") or signal_item.get("ageMs")
    try:
        ms = float(raw or 0)
    except (TypeError, ValueError):
        return 0.0
    if ms <= 0:
        return 0.0
    return ms / 3_600_000



def _signal_freshness(age_hours: float) -> str:
    if age_hours <= 0:
        return "UNKNOWN"
    if age_hours < 2:
        return "FRESH"
    if age_hours < 8:
        return "AGING"
    return "STALE"



def _audit_gate_state(audit: dict[str, Any], audit_flags: list[str]) -> tuple[str, str]:
    if not audit or not audit.get("hasResult") or not audit.get("isSupported"):
        return "WARN", "Audit coverage is partial or unavailable."

    level = _to_int(audit.get("riskLevel"))
    risk_enum = str(audit.get("riskLevelEnum") or "").upper()
    extra = audit.get("extraInfo") or {}
    combined = " ".join(str(x) for x in audit_flags).lower()

    blocked_terms = ["honeypot", "scam", "malicious", "phishing"]
    if level >= 5 or any(term in combined for term in blocked_terms):
        return "BLOCK", "Critical audit flags detected."
    if level >= 4 or risk_enum == "HIGH":
        return "BLOCK", f"Audit risk is high ({risk_enum or level})."
    if _to_float(extra.get("buyTax")) > 10 or _to_float(extra.get("sellTax")) > 10:
        return "WARN", "Token taxes are elevated above 10%."
    if audit_flags:
        return "WARN", "Audit returned structural caution flags."
    return "ALLOW", ""


def _extract_strongest_signals(signal: dict[str, Any]) -> list[str]:
    items = signal.get("data", []) or []
    if signal.get("strongest_signals"):
        return [str(x) for x in signal.get("strongest_signals", [])]
    if not items and signal.get("status"):
        return [str(signal.get("summary") or signal.get("status"))]
    out = []
    for item in items[:5]:
        ticker = item.get("ticker") or "Token"
        direction = str(item.get("direction") or "signal").upper()
        status = item.get("status") or "unknown"
        wallets = _to_int(item.get("smartMoneyCount"))
        age_hours = _signal_age_hours(item)
        age_suffix = f" {age_hours:.0f}h ago" if age_hours > 0 else ""
        if wallets > 0:
            out.append(f"{ticker} — {wallets} smart-money wallets | {direction}{' ⏱️' if status == 'timeout' else ''}{age_suffix}")
        else:
            out.append(f"{ticker}: {direction} ({status}){age_suffix}")
    return _unique(out)


def _extract_symbol_and_liquidity(item: dict[str, Any]) -> tuple[str, float]:
    symbol = str(item.get("symbol") or item.get("baseAsset") or item.get("name") or "Token")
    liquidity = _pick_number(item, "liquidity", "liquidityUsd")
    return symbol, liquidity



def _watch_liquidity_quality(liquidity: float) -> str:
    if liquidity <= 0:
        return ""
    if liquidity < 1_000_000:
        return "⚠️ very thin"
    if liquidity < 10_000_000:
        return "⚠️ thin"
    if liquidity < 50_000_000:
        return "🟡 moderate"
    return "✅ deep"


def _extract_trending_now(market_rank: dict[str, Any]) -> list[str]:
    direct = [str(x) for x in market_rank.get("trending_now", []) or []]
    if direct:
        return direct[:3]

    out: list[str] = []
    tokens = market_rank.get("data", {}).get("tokens", []) or market_rank.get("tokens", []) or []
    for item in tokens[:3]:
        symbol, liquidity = _extract_symbol_and_liquidity(item)
        search_count = _to_int(item.get("searchCount24h"))
        liq_part = f"{_human_money_short(liquidity)} liq {_watch_liquidity_quality(liquidity)}".strip() if liquidity > 0 else "liq —"
        if search_count > 0:
            out.append(f"{symbol} {search_count} searches · {liq_part}")
        else:
            out.append(f"{symbol} · {liq_part}")
    leaderboard = market_rank.get("data", {}).get("leaderBoardList", []) or market_rank.get("leaderBoardList", []) or []
    for item in leaderboard[:3]:
        symbol = item.get("symbol") or item.get("baseAsset") or item.get("name") or "Token"
        brief = item.get("socialHypeInfo", {}).get("socialSummaryBriefTranslated") or item.get("socialHypeInfo", {}).get("socialSummaryBrief")
        out.append(f"{symbol} — {brief}" if brief else str(symbol))
    return _unique(out)[:3]



def _extract_smart_money_flow(market_rank: dict[str, Any], signal: dict[str, Any]) -> list[str]:
    direct = [str(x) for x in market_rank.get("smart_money_flow", []) or []]
    if direct:
        return direct[:3]

    out: list[str] = []
    items = signal.get("data", []) or []
    for item in items[:3]:
        ticker = item.get("ticker") or "Token"
        count = _to_int(item.get("smartMoneyCount"))
        direction = str(item.get("direction") or "signal").upper()
        if count:
            out.append(f"{ticker} — {count} smart-money wallets | {direction}")
        else:
            out.append(f"{ticker} — {direction}")
    return _unique(out)[:3]



def _extract_social_hype(market_rank: dict[str, Any]) -> list[str]:
    direct = [str(x) for x in market_rank.get("social_hype", []) or []]
    if direct:
        return direct[:2]

    out: list[str] = []
    leaderboard = market_rank.get("data", {}).get("leaderBoardList", []) or market_rank.get("leaderBoardList", []) or []
    for item in leaderboard[:3]:
        symbol = item.get("symbol") or item.get("baseAsset") or item.get("name") or "Token"
        brief = item.get("socialHypeInfo", {}).get("socialSummaryBriefTranslated") or item.get("socialHypeInfo", {}).get("socialSummaryBrief")
        if brief:
            out.append(f"{symbol} — {brief}")
        else:
            out.append(f"{symbol} — social attention visible")
    if out:
        return _unique(out)[:2]

    tokens = market_rank.get("data", {}).get("tokens", []) or market_rank.get("tokens", []) or []
    for item in tokens[:2]:
        symbol = item.get("symbol") or "Token"
        search_count = _to_int(item.get("searchCount24h"))
        if search_count > 0:
            out.append(f"{symbol} — {search_count} searches in 24h")
    return _unique(out)[:2]



def _extract_meme_watch(meme_rush: dict[str, Any]) -> list[str]:
    direct = [str(x) for x in meme_rush.get("meme_watch", []) or []]
    if direct:
        return direct[:3]

    out: list[str] = []
    items = meme_rush.get("data", []) or meme_rush.get("tokens", []) or []
    for item in items[:3]:
        symbol = item.get("symbol") or item.get("name", {}).get("topicNameEn") or item.get("type") or "Token"
        progress = _pick_number(item, "progress")
        migrate = _to_int(item.get("migrateStatus"))
        if migrate == 1:
            out.append(f"{symbol} — migrated")
        elif progress >= 90:
            out.append(f"{symbol} — near migration ({progress:.0f}% bonded)")
        elif progress > 0:
            out.append(f"{symbol} — building ({progress:.0f}% bonded)")
        else:
            out.append(str(symbol))
    return _unique(out)[:3]



def _extract_top_picks(trending_now: list[str], strongest_signals: list[str], top_narratives: list[str], exchange_board: list[str] | None = None) -> list[str]:
    picks: list[str] = []
    if strongest_signals:
        picks.append(f"{strongest_signals[0]} — best visible setup")
    if trending_now:
        picks.append(f"{trending_now[0]} — strongest broad attention")
    if top_narratives:
        picks.append(f"{top_narratives[0]} — narrative worth ranking, not chasing")
    if exchange_board:
        picks.append(f"{exchange_board[0]} — exchange board anchor")
    return _unique(picks)[:3]


def _human_money_short(value: float) -> str:
    if value >= 1_000_000_000:
        return f"${value/1_000_000_000:.1f}B"
    if value >= 1_000_000:
        return f"${value/1_000_000:.1f}M"
    if value >= 1_000:
        return f"${value/1_000:.1f}K"
    if value > 0:
        return f"${value:.0f}"
    return "n/a"


def _extract_risk_zones(market_rank: dict[str, Any], meme_rush: dict[str, Any]) -> list[str]:
    zones = list(market_rank.get("risk_zones", []) or [])
    for item in meme_rush.get("data", [])[:5] or []:
        if _to_int(item.get("tagDevWashTrading")) == 1 or _to_int(item.get("tagInsiderWashTrading")) == 1:
            zones.append(f"{item.get('symbol', 'Token')} shows wash-trading related caution.")
        if _to_int(item.get("migrateStatus")) == 0 and _pick_number(item, "progress") >= 90:
            zones.append(f"{item.get('symbol', 'Token')} is near migration and may be volatile.")
    return _unique(zones)


def _first_item(value: Any) -> dict[str, Any] | None:
    if isinstance(value, list) and value:
        first = value[0]
        if isinstance(first, dict):
            return first
    return None


def _best_token_match(items: Any, symbol: str, metadata: dict[str, Any] | None = None) -> dict[str, Any] | None:
    if not isinstance(items, list):
        return metadata if metadata else None

    target = _normalize_match_key(symbol)
    target_contract = _normalize_contract((metadata or {}).get("contractAddress"))
    scored: list[tuple[int, dict[str, Any]]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        score = _token_match_score(item, target, target_contract)
        if score > 0:
            scored.append((score, item))

    if scored:
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return scored[0][1]

    return metadata if metadata else _first_item(items)


def _best_symbol_match(items: Any, target: str) -> dict[str, Any] | None:
    if not isinstance(items, list) or not target:
        return None
    scored: list[tuple[int, dict[str, Any]]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        score = _token_match_score(item, target)
        if score > 0:
            scored.append((score, item))
    if not scored:
        return None
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return scored[0][1]


def _token_match_score(item: dict[str, Any], target: str, target_contract: str = "") -> int:
    if target_contract:
        item_contract = _normalize_contract(item.get("contractAddress"))
        token_addresses = item.get("tokenAddresses") or []
        if item_contract == target_contract:
            return 200
        for entry in token_addresses:
            if isinstance(entry, dict) and _normalize_contract(entry.get("contractAddress")) == target_contract:
                return 200

    symbol_fields = ["symbol", "ticker", "tokenSymbol", "baseAsset"]
    name_fields = ["name", "tokenName", "baseAssetName"]

    for field in symbol_fields:
        if _normalize_match_key(item.get(field)) == target:
            return 120
    for field in name_fields:
        if _normalize_match_key(item.get(field)) == target:
            return 90
    for field in symbol_fields + name_fields:
        candidate = _normalize_match_key(item.get(field))
        if not candidate:
            continue
        if candidate.startswith(target) or target.startswith(candidate):
            return 40
        if target in candidate:
            return 20
    return 0


def _normalize_match_key(value: Any) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(value or "").upper())


def _normalize_contract(value: Any) -> str:
    return str(value or "").strip().lower()


def _pick_number(data: dict[str, Any], *keys: str) -> float:
    for key in keys:
        if key in data:
            return _to_float(data.get(key))
    return 0.0


def _pick_int(data: dict[str, Any], *keys: str) -> int:
    for key in keys:
        if key in data:
            return _to_int(data.get(key))
    return 0


def _to_float(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _to_int(value: Any) -> int:
    try:
        return int(float(value or 0))
    except (TypeError, ValueError):
        return 0


def _unique(items: list[str]) -> list[str]:
    out: list[str] = []
    for item in items:
        text = str(item).strip()
        if text and text not in out:
            out.append(text)
    return out


def _merge_risks(*risk_lists: list[Any]) -> list[str]:
    merged: list[str] = []
    for risk_list in risk_lists:
        for item in risk_list or []:
            text = str(item).strip()
            if text and text not in merged:
                merged.append(text)
    return merged
