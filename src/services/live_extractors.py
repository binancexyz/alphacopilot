from __future__ import annotations

from typing import Any


def extract_token_context(raw: dict[str, Any], symbol: str) -> dict[str, Any]:
    token_info = raw.get("query-token-info", {})
    market_rank = raw.get("crypto-market-rank", {})
    signal = raw.get("trading-signal", {})
    audit = raw.get("query-token-audit", {})

    return {
        "symbol": symbol,
        "display_name": token_info.get("symbol") or symbol,
        "price": token_info.get("price", 0.0),
        "liquidity": token_info.get("liquidity", 0.0),
        "holders": token_info.get("holders", 0),
        "market_rank_context": market_rank.get("summary", ""),
        "signal_status": signal.get("status", "unknown"),
        "signal_trigger_context": signal.get("summary", ""),
        "audit_flags": audit.get("flags", []),
        "major_risks": _merge_risks(
            signal.get("risks", []),
            audit.get("risks", []),
            market_rank.get("risks", []),
        ),
    }


def extract_wallet_context(raw: dict[str, Any], address: str) -> dict[str, Any]:
    address_info = raw.get("query-address-info", {})
    return {
        "address": address,
        "portfolio_value": address_info.get("portfolio_value", 0.0),
        "holdings_count": address_info.get("holdings_count", 0),
        "top_holdings": address_info.get("top_holdings", []),
        "top_concentration_pct": address_info.get("top_concentration_pct", 0.0),
        "change_24h": address_info.get("change_24h", 0.0),
        "notable_exposures": address_info.get("notable_exposures", []),
        "major_risks": address_info.get("major_risks", []),
    }


def extract_watch_today_context(raw: dict[str, Any]) -> dict[str, Any]:
    market_rank = raw.get("crypto-market-rank", {})
    meme_rush = raw.get("meme-rush", {})
    signal = raw.get("trading-signal", {})
    return {
        "top_narratives": market_rank.get("top_narratives", []) or meme_rush.get("top_narratives", []),
        "strongest_signals": signal.get("strongest_signals", []),
        "risk_zones": market_rank.get("risk_zones", []),
        "market_takeaway": market_rank.get("summary", ""),
        "major_risks": _merge_risks(market_rank.get("risks", []), meme_rush.get("risks", []), signal.get("risks", [])),
    }


def extract_signal_context(raw: dict[str, Any], token: str) -> dict[str, Any]:
    signal = raw.get("trading-signal", {})
    audit = raw.get("query-token-audit", {})
    return {
        "token": token,
        "signal_status": signal.get("status", "unknown"),
        "trigger_price": signal.get("trigger_price", 0.0),
        "current_price": signal.get("current_price", 0.0),
        "max_gain": signal.get("max_gain", 0.0),
        "exit_rate": signal.get("exit_rate", 0.0),
        "audit_flags": audit.get("flags", []),
        "supporting_context": signal.get("summary", ""),
        "major_risks": _merge_risks(signal.get("risks", []), audit.get("risks", [])),
    }


def _merge_risks(*risk_lists: list[Any]) -> list[str]:
    merged: list[str] = []
    for risk_list in risk_lists:
        for item in risk_list or []:
            text = str(item).strip()
            if text and text not in merged:
                merged.append(text)
    return merged
