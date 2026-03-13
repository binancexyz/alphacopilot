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
        elif command_key == "watchtoday":
            _run_skill(
                raw,
                "crypto-market-rank",
                lambda: _fetch_market_rank_bundle(client, base, chain_id, include_social=True, include_inflow=True, notes=notes),
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

            if command_key in {"token", "meme"}:
                market_result = _capture_skill(
                    lambda: _fetch_market_rank_bundle(client, base, chain_id, include_social=(command_key == "meme"), include_inflow=False, notes=notes),
                    failed_skills,
                    errors,
                    "crypto-market-rank",
                )
                if market_result is not None:
                    raw["crypto-market-rank"] = market_result

            if command_key in {"token", "signal", "meme"}:
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

            if command_key == "meme":
                meme_result = _capture_skill(
                    lambda: _fetch_token_meme_rush_bundle(client, base, chain_id, symbol, notes),
                    failed_skills,
                    errors,
                    "meme-rush",
                )
                if meme_result is not None:
                    raw["meme-rush"] = meme_result

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

    return (
        {
            "search": search_items,
            "metadata": metadata_json.get("data", {}),
            "dynamic": dynamic_json.get("data", {}),
            "_raw": {
                "search": search_json,
                "metadata": metadata_json,
                "dynamic": dynamic_json,
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
