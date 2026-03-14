from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4
import re

from src.config import settings
from src.services.binance_skill_mapping import COMMAND_SKILL_MAP
from src.services.skill_registry import get_skill_reference, skill_registry_snapshot
from src.utils.parsing import normalize_token_input


@dataclass(frozen=True)
class BridgeBundle:
    raw: dict[str, Any]
    meta: dict[str, Any]


def fetch_live_bundle(command: str, entity: str = "") -> BridgeBundle:
    command_key = command.strip().lower()
    skills = COMMAND_SKILL_MAP.get(command_key)
    if skills is None:
        raise ValueError(f"Unsupported command: {command}")

    httpx = _require_httpx()
    base = "https://web3.binance.com"
    chain_id = settings.bridge_default_chain_id

    raw: dict[str, Any] = {}
    failed_skills: list[str] = []
    errors: dict[str, str] = {}
    notes: list[str] = []

    with httpx.Client(timeout=settings.bridge_http_timeout_seconds, follow_redirects=True) as client:
        if command_key == "wallet":
            _run_skill(
                raw,
                "query-address-info",
                lambda: _fetch_wallet_positions(client, base, chain_id, entity),
                failed_skills,
                errors,
            )
        elif command_key == "alpha":
            symbol = normalize_token_input(entity)
            _run_skill(
                raw,
                "alpha",
                lambda: _fetch_alpha_bundle(client, base, symbol),
                failed_skills,
                errors,
            )
            token_result = _capture_skill(
                lambda: _fetch_token_info_bundle(client, base, chain_id, symbol),
                failed_skills,
                errors,
                "query-token-info",
            )
            if token_result is not None:
                raw["query-token-info"] = token_result[0]
                contract_address = token_result[1]
                audit_result = _capture_skill(
                    lambda: _fetch_audit_bundle(client, base, chain_id, contract_address),
                    failed_skills,
                    errors,
                    "query-token-audit",
                )
                if audit_result is not None:
                    raw["query-token-audit"] = audit_result
        elif command_key == "futures":
            symbol = normalize_token_input(entity)
            _run_skill(
                raw,
                "derivatives-trading-usds-futures",
                lambda: _fetch_futures_bundle(client, symbol),
                failed_skills,
                errors,
            )
            token_result = _capture_skill(
                lambda: _fetch_token_info_bundle(client, base, chain_id, symbol),
                failed_skills,
                errors,
                "query-token-info",
            )
            if token_result is not None:
                raw["query-token-info"] = token_result[0]
        elif command_key == "watchtoday":
            _run_skill(
                raw,
                "crypto-market-rank",
                lambda: _fetch_market_rank_bundle(client, base, chain_id, include_social=True, include_inflow=True, include_pnl_rank=True, notes=notes),
                failed_skills,
                errors,
            )
            _run_skill(
                raw,
                "trading-signal",
                lambda: _fetch_signal_board(client, base, chain_id),
                failed_skills,
                errors,
            )
            _run_skill(
                raw,
                "meme-rush",
                lambda: _fetch_watchtoday_meme_rush_bundle(client, base, chain_id, notes),
                failed_skills,
                errors,
            )
            _run_skill(
                raw,
                "derivatives-trading-usds-futures",
                lambda: _fetch_futures_watchtoday_bundle(client, notes),
                failed_skills,
                errors,
            )
        elif command_key == "portfolio":
            _run_skill(
                raw,
                "assets",
                lambda: _fetch_assets_portfolio(client),
                failed_skills,
                errors,
            )
            _run_skill(
                raw,
                "margin-trading",
                lambda: _fetch_margin_account(client),
                failed_skills,
                errors,
            )
        else:
            symbol = normalize_token_input(entity)
            token_payload: dict[str, Any] | None = None
            contract_address = ""

            token_result = _capture_skill(
                lambda: _fetch_token_info_bundle(client, base, chain_id, symbol),
                failed_skills,
                errors,
                "query-token-info",
            )
            if token_result is not None:
                token_payload, contract_address = token_result
                raw["query-token-info"] = token_payload

            if command_key in {"token", "meme", "signal"}:
                market_result = _capture_skill(
                    lambda: _fetch_market_rank_bundle(
                        client,
                        base,
                        chain_id,
                        include_social=(command_key in {"meme", "signal"}),
                        include_inflow=(command_key in {"token", "signal"}),
                        notes=notes,
                    ),
                    failed_skills,
                    errors,
                    "crypto-market-rank",
                )
                if market_result is not None:
                    raw["crypto-market-rank"] = market_result

            if command_key in {"token", "signal", "meme", "audit"}:
                signal_result = _capture_skill(
                    lambda: _fetch_token_signal_bundle(client, base, chain_id, symbol, contract_address),
                    failed_skills,
                    errors,
                    "trading-signal",
                )
                if signal_result is not None:
                    raw["trading-signal"] = signal_result

            if command_key in {"token", "signal", "audit", "meme"}:
                audit_result = _capture_skill(
                    lambda: _fetch_audit_bundle(client, base, chain_id, contract_address),
                    failed_skills,
                    errors,
                    "query-token-audit",
                )
                if audit_result is not None:
                    raw["query-token-audit"] = audit_result

            if command_key == "meme" or (command_key == "token" and _looks_like_meme_candidate(symbol, token_payload)):
                meme_result = _capture_skill(
                    lambda: _fetch_token_meme_rush_bundle(client, base, chain_id, symbol, notes),
                    failed_skills,
                    errors,
                    "meme-rush",
                )
                if meme_result is not None:
                    raw["meme-rush"] = meme_result

            if command_key in {"token", "alpha"}:
                spot_result = _capture_skill(
                    lambda: _fetch_spot_bundle(client, symbol, notes),
                    failed_skills,
                    errors,
                    "spot",
                )
                if spot_result is not None:
                    raw["spot"] = spot_result

            if command_key in {"token"}:
                alpha_result = _capture_skill(
                    lambda: _fetch_alpha_bundle(client, base, symbol),
                    failed_skills,
                    errors,
                    "alpha",
                )
                if alpha_result is not None:
                    raw["alpha"] = alpha_result

            if command_key in {"token", "signal"}:
                futures_result = _capture_skill(
                    lambda: _fetch_futures_bundle(client, symbol),
                    failed_skills,
                    errors,
                    "derivatives-trading-usds-futures",
                )
                if futures_result is not None:
                    raw["derivatives-trading-usds-futures"] = futures_result

    if not raw and failed_skills:
        notes.insert(0, "No live skill calls succeeded for this request.")
    elif failed_skills:
        notes.insert(0, f"Partial live bundle returned with {len(failed_skills)} failed skill call(s).")

    return BridgeBundle(
        raw=raw,
        meta={
            "source": "bibipilot-bridge",
            "skills": list(skills),
            "status": "partial-live" if failed_skills else "live-ok",
            "failedSkills": failed_skills,
            "errors": errors,
            "notes": notes,
            "skillRefs": skill_registry_snapshot(list(skills)),
        },
    )


def _run_skill(
    raw: dict[str, Any],
    skill_name: str,
    loader,
    failed_skills: list[str],
    errors: dict[str, str],
) -> None:
    payload = _capture_skill(loader, failed_skills, errors, skill_name)
    if payload is not None:
        raw[skill_name] = payload


def _capture_skill(loader, failed_skills: list[str], errors: dict[str, str], skill_name: str):
    try:
        return loader()
    except Exception as exc:
        if skill_name not in failed_skills:
            failed_skills.append(skill_name)
        errors[skill_name] = _short_error(exc)
        return None


def _looks_like_meme_candidate(symbol: str, token_payload: dict[str, Any] | None) -> bool:
    if not token_payload:
        return False

    known_meme_symbols = {"DOGE", "SHIB", "PEPE", "BONK", "FLOKI", "WIF"}
    if symbol.upper() in known_meme_symbols:
        return True

    metadata = token_payload.get("metadata", {}) if isinstance(token_payload, dict) else {}
    search = token_payload.get("search", []) if isinstance(token_payload, dict) else []
    tag_values: list[str] = []
    for source in ((metadata.get("tokenTag") or {}), *((item.get("tokenTag") or {}) for item in search if isinstance(item, dict))):
        if isinstance(source, dict):
            tag_values.extend(str(key).lower() for key in source.keys())

    return any(tag in {"meme", "community", "dog", "frog"} for tag in tag_values)


def _fetch_wallet_positions(client, base: str, chain_id: str, address: str) -> dict[str, Any]:
    return _fetch_json(
        client,
        "GET",
        f"{base}/bapi/defi/v3/public/wallet-direct/buw/wallet/address/pnl/active-position-list",
        "query-address-info",
        headers=_skill_headers(
            "query-address-info",
            {
                "clienttype": "web",
                "clientversion": "1.2.0",
            },
        ),
        params={"address": address, "chainId": chain_id, "offset": 0},
    )


def _fetch_token_kline(client, chain_id: str, contract_address: str, interval: str = "4h", limit: int = 100) -> dict[str, Any]:
    platform_map = {"56": "bsc", "1": "ethereum", "CT_501": "solana", "8453": "base"}
    platform = platform_map.get(str(chain_id))
    if not platform or not contract_address:
        return {}
    return _fetch_json(
        client,
        "GET",
        "https://dquery.sintral.io/u-kline/v1/k-line/candles",
        "query-token-info",
        headers=_skill_headers("query-token-info"),
        params={"address": contract_address, "platform": platform, "interval": interval, "limit": limit}
    )


def _fetch_token_info_bundle(client, base: str, chain_id: str, symbol: str) -> tuple[dict[str, Any], str]:
    search_json = _fetch_json(
        client,
        "GET",
        f"{base}/bapi/defi/v5/public/wallet-direct/buw/wallet/market/token/search",
        "query-token-info",
        headers=_skill_headers("query-token-info"),
        params={"keyword": symbol, "chainIds": chain_id, "orderBy": "volume24h"},
    )
    search_items = search_json.get("data") or []
    first = _first_matching_token(search_items, symbol)
    if not first:
        raise LookupError(f"Token not found in live search: {symbol}")

    contract = str(first.get("contractAddress") or "").strip()
    if not contract:
        raise LookupError(f"Resolved token is missing contract address: {symbol}")

    metadata_json = _fetch_json(
        client,
        "GET",
        f"{base}/bapi/defi/v1/public/wallet-direct/buw/wallet/dex/market/token/meta/info",
        "query-token-info",
        headers=_skill_headers("query-token-info"),
        params={"chainId": chain_id, "contractAddress": contract},
    )
    dynamic_json = _fetch_json(
        client,
        "GET",
        f"{base}/bapi/defi/v4/public/wallet-direct/buw/wallet/market/token/dynamic/info",
        "query-token-info",
        headers=_skill_headers("query-token-info"),
        params={"chainId": chain_id, "contractAddress": contract},
    )

    kline_json = {}
    try:
        kline_json = _fetch_token_kline(client, chain_id, contract)
    except Exception:
        pass

    return (
        {
            "search": search_items,
            "metadata": metadata_json.get("data", {}),
            "dynamic": dynamic_json.get("data", {}),
            "kline": kline_json.get("data", []),
            "_raw": {
                "search": search_json,
                "metadata": metadata_json,
                "dynamic": dynamic_json,
                "kline": kline_json,
            },
        },
        contract,
    )


def _fetch_token_signal_bundle(client, base: str, chain_id: str, symbol: str, contract: str = "") -> dict[str, Any]:
    signal_json = _fetch_signal_board(client, base, chain_id)
    signal_items = signal_json.get("data") or []
    signal_matches = _matching_signal_items(signal_items, symbol, contract)
    return {
        "data": signal_matches,
        "_raw": signal_json,
    }


def _fetch_signal_board(client, base: str, chain_id: str) -> dict[str, Any]:
    return _fetch_json(
        client,
        "POST",
        f"{base}/bapi/defi/v1/public/wallet-direct/buw/wallet/web/signal/smart-money",
        "trading-signal",
        headers=_skill_headers("trading-signal", {"Content-Type": "application/json"}),
        json_body={"smartSignalType": "", "page": 1, "pageSize": 100, "chainId": chain_id},
    )


def _fetch_audit_bundle(client, base: str, chain_id: str, contract: str) -> dict[str, Any]:
    if not contract:
        raise ValueError("Audit requires a resolved contract address.")
    return _fetch_json(
        client,
        "POST",
        f"{base}/bapi/defi/v1/public/wallet-direct/security/token/audit",
        "query-token-audit",
        headers=_skill_headers(
            "query-token-audit",
            {
                "Content-Type": "application/json",
                "source": "agent",
            },
        ),
        json_body={"binanceChainId": chain_id, "contractAddress": contract, "requestId": str(uuid4())},
    )


def _fetch_market_rank_bundle(
    client,
    base: str,
    chain_id: str,
    *,
    include_social: bool,
    include_inflow: bool,
    include_pnl_rank: bool = False,
    notes: list[str],
) -> dict[str, Any]:
    unified_json = _fetch_json(
        client,
        "POST",
        f"{base}/bapi/defi/v1/public/wallet-direct/buw/wallet/market/token/pulse/unified/rank/list",
        "crypto-market-rank",
        headers=_skill_headers("crypto-market-rank", {"Content-Type": "application/json"}),
        json_body={"rankType": 10, "chainId": chain_id, "period": 50, "sortBy": 70, "orderAsc": False, "page": 1, "size": 20},
    )

    out: dict[str, Any] = {
        "data": {
            "tokens": unified_json.get("data", {}).get("tokens", []) or [],
        },
        "_raw": {
            "unifiedRank": unified_json,
        },
    }

    if include_social:
        try:
            social_json = _fetch_json(
                client,
                "GET",
                f"{base}/bapi/defi/v1/public/wallet-direct/buw/wallet/market/token/pulse/social/hype/rank/leaderboard",
                "crypto-market-rank",
                headers=_skill_headers("crypto-market-rank"),
                params={"chainId": chain_id, "sentiment": "All", "socialLanguage": "ALL", "targetLanguage": "en", "timeRange": 1},
            )
            out["data"]["leaderBoardList"] = social_json.get("data", {}).get("leaderBoardList", []) or []
            out["_raw"]["socialHypeLeaderboard"] = social_json
        except Exception as exc:
            notes.append(f"crypto-market-rank social hype call failed: {_short_error(exc)}")

    if include_inflow:
        try:
            inflow_json = _fetch_json(
                client,
                "POST",
                f"{base}/bapi/defi/v1/public/wallet-direct/tracker/wallet/token/inflow/rank/query",
                "crypto-market-rank",
                headers=_skill_headers("crypto-market-rank", {"Content-Type": "application/json"}),
                json_body={"chainId": chain_id, "period": "24h", "tagType": 2},
            )
            out["smart_money_inflow"] = inflow_json.get("data", []) or []
            out["_raw"]["smartMoneyInflowRank"] = inflow_json
        except Exception as exc:
            notes.append(f"crypto-market-rank inflow call failed: {_short_error(exc)}")

    if include_pnl_rank:
        try:
            pnl_json = _fetch_address_pnl_rank(client, base, chain_id)
            pnl_data = pnl_json.get("data", {})
            out["top_traders"] = pnl_data.get("data", []) or []
            out["_raw"]["addressPnlRank"] = pnl_json
        except Exception as exc:
            notes.append(f"crypto-market-rank address PnL call failed: {_short_error(exc)}")

    return out


def _fetch_watchtoday_meme_rush_bundle(client, base: str, chain_id: str, notes: list[str]) -> dict[str, Any]:
    tokens: list[dict[str, Any]] = []
    topics: list[dict[str, Any]] = []
    raw_parts: dict[str, Any] = {}

    try:
        rank_json = _fetch_meme_rank_list(client, base, chain_id, rank_type=20)
        tokens = rank_json.get("data", []) or []
        raw_parts["rankList"] = rank_json
    except Exception as exc:
        notes.append(f"meme-rush rank list call failed: {_short_error(exc)}")

    try:
        topic_json = _fetch_topic_rush_list(client, base, chain_id, rank_type=30, sort=30)
        topics = topic_json.get("data", []) or []
        raw_parts["topicRush"] = topic_json
    except Exception as exc:
        notes.append(f"meme-rush topic rush call failed: {_short_error(exc)}")

    if not tokens and not topics:
        raise RuntimeError("meme-rush returned neither token ranks nor topic ranks.")

    return {
        "tokens": tokens,
        "topics": topics,
        "_raw": raw_parts,
    }


def _fetch_token_meme_rush_bundle(client, base: str, chain_id: str, symbol: str, notes: list[str]) -> dict[str, Any]:
    token_lists: list[dict[str, Any]] = []
    raw_parts: dict[str, Any] = {}

    for rank_type in (10, 20, 30):
        try:
            rank_json = _fetch_meme_rank_list(client, base, chain_id, rank_type=rank_type)
            raw_parts[f"rankType{rank_type}"] = rank_json
            token_lists.extend(rank_json.get("data", []) or [])
        except Exception as exc:
            notes.append(f"meme-rush rankType={rank_type} failed: {_short_error(exc)}")

    if not token_lists:
        raise RuntimeError("meme-rush token rank lists are unavailable.")

    matched = _matching_symbol_entries(token_lists, symbol)
    deduped = _dedupe_token_entries(matched or token_lists)
    return {
        "data": deduped,
        "tokens": deduped,
        "_raw": raw_parts,
    }


def _fetch_meme_rank_list(client, base: str, chain_id: str, *, rank_type: int) -> dict[str, Any]:
    return _fetch_json(
        client,
        "POST",
        f"{base}/bapi/defi/v1/public/wallet-direct/buw/wallet/market/token/pulse/rank/list",
        "meme-rush",
        headers=_skill_headers("meme-rush", {"Content-Type": "application/json"}),
        json_body={"chainId": chain_id, "rankType": rank_type, "limit": 40},
    )


def _fetch_topic_rush_list(client, base: str, chain_id: str, *, rank_type: int, sort: int) -> dict[str, Any]:
    return _fetch_json(
        client,
        "GET",
        f"{base}/bapi/defi/v1/public/wallet-direct/buw/wallet/market/token/social-rush/rank/list",
        "meme-rush",
        headers=_skill_headers("meme-rush"),
        params={"chainId": chain_id, "rankType": rank_type, "sort": sort, "asc": "false"},
    )


# ---------- Address PnL Leaderboard (crypto-market-rank API 5) ----------


def _fetch_address_pnl_rank(client, base: str, chain_id: str, *, period: str = "7d", tag: str = "ALL") -> dict[str, Any]:
    return _fetch_json(
        client,
        "GET",
        f"{base}/bapi/defi/v1/public/wallet-direct/market/leaderboard/query",
        "crypto-market-rank",
        headers=_skill_headers("crypto-market-rank"),
        params={"chainId": chain_id, "period": period, "tag": tag, "pageNo": 1, "pageSize": 10, "sortBy": 0, "orderBy": 0},
    )


# ---------- Alpha skill fetchers (public, no auth) ----------


def _fetch_alpha_token_list(client, base: str) -> dict[str, Any]:
    return _fetch_json(
        client,
        "GET",
        f"{base}/bapi/defi/v1/public/wallet-direct/buw/wallet/cex/alpha/all/token/list",
        "alpha",
        headers=_skill_headers("alpha"),
    )


def _fetch_alpha_ticker(client, base: str, symbol: str) -> dict[str, Any]:
    return _fetch_json(
        client,
        "GET",
        f"{base}/bapi/defi/v1/public/alpha-trade/ticker",
        "alpha",
        headers=_skill_headers("alpha"),
        params={"symbol": symbol},
    )


def _fetch_alpha_bundle(client, base: str, symbol: str) -> dict[str, Any]:
    token_list_json = _fetch_alpha_token_list(client, base)
    token_list_items = token_list_json.get("data") or []
    alpha_symbol = _resolve_alpha_symbol(token_list_items, symbol)

    out: dict[str, Any] = {
        "token_list": token_list_items,
        "is_alpha_listed": alpha_symbol is not None,
        "_raw": {"tokenList": token_list_json},
    }

    if alpha_symbol:
        try:
            ticker_json = _fetch_alpha_ticker(client, base, alpha_symbol)
            out["ticker"] = ticker_json.get("data", ticker_json)
            out["_raw"]["ticker"] = ticker_json
        except Exception:
            pass

        try:
            kline_json = _fetch_alpha_kline(client, base, alpha_symbol)
            out["kline"] = kline_json.get("data", [])
            out["_raw"]["kline"] = kline_json
        except Exception:
            pass

    return out

def _fetch_alpha_kline(client, base: str, symbol: str, interval: str = "4h", limit: int = 20) -> dict[str, Any]:
    return _fetch_json(
        client,
        "GET",
        f"{base}/bapi/defi/v1/public/alpha-trade/klines",
        "alpha",
        headers=_skill_headers("alpha"),
        params={"symbol": symbol.upper(), "interval": interval, "limit": limit},
    )


def _resolve_alpha_symbol(token_list: list[dict[str, Any]], symbol: str) -> str | None:
    target = _normalize_match_key(symbol)
    for item in token_list:
        item_symbol = str(item.get("symbol") or item.get("ticker") or "")
        if _normalize_match_key(item_symbol) == target:
            return str(item.get("symbol") or item_symbol)
        item_name = str(item.get("name") or item.get("tokenName") or "")
        if _normalize_match_key(item_name) == target:
            return str(item.get("symbol") or item_symbol)
    return None


# ---------- Portfolio skill fetchers (authenticated) ----------

import hmac
import hashlib
import time
from urllib.parse import urlencode

def _fetch_signed_json(
    client,
    method: str,
    base: str,
    path: str,
    skill_name: str,
    *,
    headers: dict[str, str],
    params: dict[str, Any] | None = None,
) -> Any:
    api_key = settings.binance_api_key.strip()
    api_secret = settings.binance_api_secret.strip()
    if not api_key or not api_secret:
        raise RuntimeError(f"{skill_name} requires BINANCE_API_KEY and BINANCE_API_SECRET")

    payload = dict(params or {})
    payload.setdefault("timestamp", int(time.time() * 1000))
    payload.setdefault("recvWindow", 10000)
    query = urlencode(payload)
    signature = hmac.new(api_secret.encode("utf-8"), query.encode("utf-8"), hashlib.sha256).hexdigest()

    auth_headers = dict(headers)
    auth_headers["X-MBX-APIKEY"] = api_key

    url = f"{base}{path}?{query}&signature={signature}"
    response = client.request(method, url, headers=auth_headers)
    response.raise_for_status()
    return response.json()

def _fetch_assets_portfolio(client) -> dict[str, Any]:
    base = "https://api.binance.com"
    payload = _fetch_signed_json(
        client,
        "POST",
        base,
        "/sapi/v3/asset/getUserAsset",
        "assets",
        headers=_skill_headers("assets"),
    )
    # The /sapi/v3/asset/getUserAsset endpoint returns a list directly, 
    # but _fetch_json enforces a dict return unless we bypass it.
    # However, _fetch_json actually just does response.json(). 
    # Let's handle the list return properly.
    return {"data": payload} if isinstance(payload, list) else payload

def _fetch_margin_account(client) -> dict[str, Any]:
    base = "https://api.binance.com"
    return _fetch_signed_json(
        client,
        "GET",
        base,
        "/sapi/v1/margin/account",
        "margin-trading",
        headers=_skill_headers("margin-trading"),
    )


# ---------- Spot skill fetchers (public, no auth) ----------


def _fetch_spot_ticker_24h(client, symbol: str) -> dict[str, Any]:
    spot_symbol = f"{symbol.upper()}USDT"
    response = client.get(
        "https://api.binance.com/api/v3/ticker/24hr",
        params={"symbol": spot_symbol},
        headers={"User-Agent": "binance-spot/1.0.2 (Skill)", "Accept-Encoding": "identity"},
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError(f"spot ticker returned non-object JSON: {type(payload).__name__}")
    return payload


def _fetch_spot_depth(client, symbol: str, limit: int = 100) -> dict[str, Any]:
    spot_symbol = f"{symbol.upper()}USDT"
    response = client.get(
        "https://api.binance.com/api/v3/depth",
        params={"symbol": spot_symbol, "limit": limit},
        headers={"User-Agent": "binance-spot/1.0.2 (Skill)", "Accept-Encoding": "identity"},
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError(f"spot depth returned non-object JSON: {type(payload).__name__}")
    return payload


def _fetch_spot_bundle(client, symbol: str, notes: list[str]) -> dict[str, Any]:
    out = {}
    
    try:
        out["ticker"] = _fetch_spot_ticker_24h(client, symbol)
    except Exception as exc:
        notes.append(f"spot ticker failed: {_short_error(exc)}")
        
    try:
        out["depth"] = _fetch_spot_depth(client, symbol)
    except Exception:
        pass
        
    try:
        out["kline"] = _fetch_spot_kline(client, symbol)
    except Exception:
        pass
        
    try:
        out["recent_trades"] = _fetch_spot_trades(client, symbol)
    except Exception:
        pass
        
    return out

def _fetch_spot_kline(client, symbol: str, interval: str = "4h", limit: int = 20) -> dict[str, Any]:
    spot_symbol = f"{symbol.upper()}USDT"
    response = client.get(
        "https://api.binance.com/api/v3/klines",
        params={"symbol": spot_symbol, "interval": interval, "limit": limit},
        headers={"User-Agent": "binance-spot/1.0.2 (Skill)", "Accept-Encoding": "identity"},
    )
    response.raise_for_status()
    payload = response.json()
    return {"data": payload} if isinstance(payload, list) else payload

def _fetch_spot_trades(client, symbol: str, limit: int = 20) -> dict[str, Any]:
    spot_symbol = f"{symbol.upper()}USDT"
    response = client.get(
        "https://api.binance.com/api/v3/trades",
        params={"symbol": spot_symbol, "limit": limit},
        headers={"User-Agent": "binance-spot/1.0.2 (Skill)", "Accept-Encoding": "identity"},
    )
    response.raise_for_status()
    payload = response.json()
    return {"data": payload} if isinstance(payload, list) else payload


# ---------- Futures skill fetchers (public, no auth) ----------

_FAPI_BASE = "https://fapi.binance.com"
_FUTURES_HEADERS = {"User-Agent": "binance-derivatives-trading-usds-futures/1.0.0 (Skill)", "Accept-Encoding": "identity"}


def _fetch_futures_funding_rate(client, symbol: str) -> dict[str, Any]:
    response = client.get(
        f"{_FAPI_BASE}/fapi/v1/fundingRate",
        params={"symbol": f"{symbol.upper()}USDT", "limit": 3},
        headers=_FUTURES_HEADERS,
    )
    response.raise_for_status()
    payload = response.json()
    return {"data": payload} if isinstance(payload, list) else payload


def _fetch_futures_open_interest(client, symbol: str) -> dict[str, Any]:
    response = client.get(
        f"{_FAPI_BASE}/fapi/v1/openInterest",
        params={"symbol": f"{symbol.upper()}USDT"},
        headers=_FUTURES_HEADERS,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError(f"futures openInterest returned non-object JSON: {type(payload).__name__}")
    return payload


def _fetch_futures_long_short_ratio(client, symbol: str) -> dict[str, Any]:
    response = client.get(
        f"{_FAPI_BASE}/futures/data/globalLongShortAccountRatio",
        params={"symbol": f"{symbol.upper()}USDT", "period": "1h", "limit": 5},
        headers=_FUTURES_HEADERS,
    )
    response.raise_for_status()
    payload = response.json()
    return {"data": payload} if isinstance(payload, list) else payload


def _fetch_futures_mark_price(client, symbol: str) -> dict[str, Any]:
    response = client.get(
        f"{_FAPI_BASE}/fapi/v1/premiumIndex",
        params={"symbol": f"{symbol.upper()}USDT"},
        headers=_FUTURES_HEADERS,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError(f"futures premiumIndex returned non-object JSON: {type(payload).__name__}")
    return payload


def _fetch_futures_taker_volume(client, symbol: str) -> dict[str, Any]:
    response = client.get(
        f"{_FAPI_BASE}/futures/data/takerlongshortRatio",
        params={"symbol": f"{symbol.upper()}USDT", "period": "1d", "limit": 1},
        headers=_FUTURES_HEADERS,
    )
    response.raise_for_status()
    payload = response.json()
    return {"data": payload} if isinstance(payload, list) else payload


def _fetch_futures_top_trader_ls(client, symbol: str) -> dict[str, Any]:
    response = client.get(
        f"{_FAPI_BASE}/futures/data/topLongShortPositionRatio",
        params={"symbol": f"{symbol.upper()}USDT", "period": "1d", "limit": 1},
        headers=_FUTURES_HEADERS,
    )
    response.raise_for_status()
    payload = response.json()
    return {"data": payload} if isinstance(payload, list) else payload


def _fetch_futures_bundle(client, symbol: str) -> dict[str, Any]:
    out: dict[str, Any] = {"_raw": {}}

    try:
        mark = _fetch_futures_mark_price(client, symbol)
        out["mark_price"] = mark
        out["_raw"]["markPrice"] = mark
    except Exception:
        pass

    try:
        funding = _fetch_futures_funding_rate(client, symbol)
        out["funding_rate"] = funding
        out["_raw"]["fundingRate"] = funding
    except Exception:
        pass

    try:
        oi = _fetch_futures_open_interest(client, symbol)
        out["open_interest"] = oi
        out["_raw"]["openInterest"] = oi
    except Exception:
        pass

    try:
        ls = _fetch_futures_long_short_ratio(client, symbol)
        out["long_short_ratio"] = ls
        out["_raw"]["longShortRatio"] = ls
    except Exception:
        pass

    try:
        taker = _fetch_futures_taker_volume(client, symbol)
        out["taker_volume"] = taker
        out["_raw"]["takerVolume"] = taker
    except Exception:
        pass

    try:
        top_ls = _fetch_futures_top_trader_ls(client, symbol)
        out["top_trader_ls"] = top_ls
        out["_raw"]["topTraderLS"] = top_ls
    except Exception:
        pass

    try:
        kline = _fetch_futures_kline(client, symbol)
        out["kline"] = kline
        out["_raw"]["kline"] = kline
    except Exception:
        pass

    try:
        ticker = _fetch_futures_ticker_24h(client, symbol)
        out["ticker"] = ticker
        out["_raw"]["ticker"] = ticker
    except Exception:
        pass

    if not out.get("mark_price") and not out.get("funding_rate"):
        raise RuntimeError(f"No futures data returned for {symbol}")

    return out

def _fetch_futures_kline(client, symbol: str, interval: str = "4h", limit: int = 20) -> dict[str, Any]:
    response = client.get(
        f"{_FAPI_BASE}/fapi/v1/klines",
        params={"symbol": f"{symbol.upper()}USDT", "interval": interval, "limit": limit},
        headers=_FUTURES_HEADERS,
    )
    response.raise_for_status()
    payload = response.json()
    return {"data": payload} if isinstance(payload, list) else payload

def _fetch_futures_ticker_24h(client, symbol: str) -> dict[str, Any]:
    response = client.get(
        f"{_FAPI_BASE}/fapi/v1/ticker/24hr",
        params={"symbol": f"{symbol.upper()}USDT"},
        headers=_FUTURES_HEADERS,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError(f"futures ticker returned non-object JSON: {type(payload).__name__}")
    return payload


def _fetch_futures_watchtoday_bundle(client, notes: list[str]) -> dict[str, Any]:
    out: dict[str, Any] = {"_raw": {}}
    top_symbols = ["BTC", "ETH", "BNB", "SOL"]
    for sym in top_symbols:
        try:
            mark = _fetch_futures_mark_price(client, sym)
            funding = _fetch_futures_funding_rate(client, sym)
            rate_items = funding.get("data", []) if isinstance(funding.get("data"), list) else []
            last_rate = float(rate_items[-1].get("fundingRate", 0)) if rate_items else 0.0
            out[sym] = {
                "mark_price": float(mark.get("markPrice", 0)),
                "index_price": float(mark.get("indexPrice", 0)),
                "funding_rate": last_rate,
            }
        except Exception as exc:
            notes.append(f"futures {sym} data failed: {_short_error(exc)}")
    if not out or all(k.startswith("_") for k in out):
        raise RuntimeError("No futures data returned for watchtoday.")
    return out


def _fetch_json(
    client,
    method: str,
    url: str,
    skill_name: str,
    *,
    headers: dict[str, str],
    params: dict[str, Any] | None = None,
    json_body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if method.upper() == "GET":
        response = client.get(url, params=params, headers=headers)
    else:
        response = client.post(url, json=json_body, headers=headers)

    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError(f"{skill_name} returned non-object JSON: {type(payload).__name__}")

    code = str(payload.get("code") or "000000")
    success = payload.get("success")
    if success is False or code not in {"000000", "0"}:
        message = payload.get("message") or payload.get("messageDetail") or payload.get("msg") or "unknown error"
        raise RuntimeError(f"{skill_name} upstream error {code}: {message}")
    return payload


def _skill_headers(skill_name: str, extra: dict[str, str] | None = None) -> dict[str, str]:
    ref = get_skill_reference(skill_name)
    headers = {
        "Accept-Encoding": "identity",
        "User-Agent": ref.user_agent or "binance-web3/1.0 (Skill)",
    }
    if extra:
        headers.update(extra)
    return headers


def _short_error(exc: Exception) -> str:
    text = " ".join(str(exc).split())
    if len(text) <= 180:
        return text
    return text[:177].rstrip() + "..."


def _matching_symbol_entries(items: list[dict[str, Any]], symbol: str) -> list[dict[str, Any]]:
    target = _normalize_match_key(symbol)
    return [item for item in items if _token_match_score(item, target) > 0]


def _dedupe_token_entries(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for item in items:
        contract = _normalize_contract(item.get("contractAddress"))
        symbol = _normalize_match_key(item.get("symbol") or item.get("ticker") or item.get("name"))
        key = contract or symbol
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def _require_httpx():
    try:
        import httpx  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError("httpx is required for live bridge mode") from exc
    return httpx


def _first_matching_token(items: list[dict[str, Any]], symbol: str) -> dict[str, Any] | None:
    if not items:
        return None

    target = _normalize_match_key(symbol)
    scored: list[tuple[int, dict[str, Any]]] = []
    for item in items:
        score = _token_match_score(item, target)
        if score > 0:
            scored.append((score, item))

    if scored:
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return scored[0][1]

    return items[0]


def _matching_signal_items(items: list[dict[str, Any]], symbol: str, contract: str | None) -> list[dict[str, Any]]:
    target_symbol = _normalize_match_key(symbol)
    target_contract = _normalize_contract(contract)
    contract_matches: list[dict[str, Any]] = []
    symbol_matches: list[dict[str, Any]] = []

    for item in items:
        item_symbol = _normalize_match_key(_pick_value(item, "ticker", "symbol", "tokenSymbol", "baseAsset"))
        item_contract = _normalize_contract(_pick_value(item, "contractAddress", "address", "tokenAddress"))

        if target_contract and item_contract == target_contract:
            contract_matches.append(item)
        if item_symbol == target_symbol:
            symbol_matches.append(item)

    if contract_matches:
        narrowed = [item for item in contract_matches if _normalize_match_key(_pick_value(item, "ticker", "symbol", "tokenSymbol", "baseAsset")) == target_symbol]
        return narrowed or contract_matches

    return symbol_matches


def _token_match_score(item: dict[str, Any], target: str) -> int:
    exact_symbol_fields = ["symbol", "ticker", "tokenSymbol", "baseAsset"]
    exact_name_fields = ["name", "tokenName", "baseAssetName"]

    for field in exact_symbol_fields:
        if _normalize_match_key(item.get(field)) == target:
            return 100

    for field in exact_name_fields:
        if _normalize_match_key(item.get(field)) == target:
            return 80

    for field in exact_symbol_fields + exact_name_fields:
        candidate = _normalize_match_key(item.get(field))
        if candidate.startswith(target) or target.startswith(candidate):
            return 40
        if target and target in candidate:
            return 20

    return 0


def _pick_value(item: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = item.get(key)
        if value not in (None, ""):
            return value
    return None


def _normalize_match_key(value: Any) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(value or "").upper())


def _normalize_contract(value: Any) -> str:
    return str(value or "").strip().lower()
