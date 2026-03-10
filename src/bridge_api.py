from __future__ import annotations

from datetime import datetime, UTC
from typing import Any
from uuid import uuid4
import re

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from src.config import settings
from src.services.binance_skill_mapping import SIGNAL_SKILLS, TOKEN_SKILLS, WALLET_SKILLS, WATCH_TODAY_SKILLS
from src.utils.parsing import normalize_token_input

app = FastAPI(title="Binance Alpha Copilot Live Bridge", version="0.2.0")


class BridgeMeta(BaseModel):
    source: str = "alpha-copilot-bridge"
    generatedAt: str
    skills: list[str] = Field(default_factory=list)
    status: str = "not-implemented"
    notes: list[str] = Field(default_factory=list)


class BridgeResponse(BaseModel):
    command: str
    entity: str = ""
    raw: dict[str, Any] = Field(default_factory=dict)
    meta: BridgeMeta


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "bridge",
        "mode": "live-enabled" if settings.bridge_live_enabled else "scaffold",
    }


@app.get("/runtime", response_model=BridgeResponse)
def runtime(
    command: str = Query(..., description="token|signal|wallet|watchtoday"),
    entity: str = Query("", description="symbol or address when relevant"),
) -> BridgeResponse:
    command_key = command.strip().lower()
    skills = _skills_for(command_key)
    if skills is None:
        raise HTTPException(status_code=400, detail=f"Unsupported command: {command}")

    if command_key in {"token", "signal"} and not entity:
        raise HTTPException(status_code=400, detail=f"command={command_key} requires entity")
    if command_key == "wallet" and not entity:
        raise HTTPException(status_code=400, detail="command=wallet requires entity")

    if settings.bridge_live_enabled and command_key == "token":
        raw = _fetch_live_token_bundle(entity)
        return BridgeResponse(
            command=command_key,
            entity=entity,
            raw=raw,
            meta=BridgeMeta(
                generatedAt=datetime.now(UTC).isoformat(),
                skills=skills,
                status="partial-live",
                notes=["Live token bridge is enabled.", "Other commands remain scaffolded until implemented."],
            ),
        )

    return BridgeResponse(
        command=command_key,
        entity=entity,
        raw={},
        meta=BridgeMeta(
            generatedAt=datetime.now(UTC).isoformat(),
            skills=skills,
            notes=[
                "This is the bridge scaffold only.",
                "Enable BRIDGE_LIVE_ENABLED=true for the first real token bridge path.",
            ],
        ),
    )


def _fetch_live_token_bundle(entity: str) -> dict[str, Any]:
    httpx = _require_httpx()
    base = "https://web3.binance.com"
    chain_id = settings.bridge_default_chain_id
    symbol = normalize_token_input(entity)
    common_headers = {"Accept-Encoding": "identity", "User-Agent": "binance-web3/1.0 (Skill)"}

    with httpx.Client(timeout=20.0, follow_redirects=True) as client:
        search_resp = client.get(
            f"{base}/bapi/defi/v5/public/wallet-direct/buw/wallet/market/token/search",
            params={"keyword": symbol, "chainIds": chain_id, "orderBy": "volume24h"},
            headers=common_headers,
        )
        search_resp.raise_for_status()
        search_json = search_resp.json()
        search_items = search_json.get("data") or []
        first = _first_matching_token(search_items, symbol)
        if not first:
            raise HTTPException(status_code=404, detail=f"Token not found in live search: {symbol}")

        contract = first.get("contractAddress")
        metadata_resp = client.get(
            f"{base}/bapi/defi/v1/public/wallet-direct/buw/wallet/dex/market/token/meta/info",
            params={"chainId": chain_id, "contractAddress": contract},
            headers=common_headers,
        )
        metadata_resp.raise_for_status()
        metadata_json = metadata_resp.json()

        dynamic_resp = client.get(
            f"{base}/bapi/defi/v4/public/wallet-direct/buw/wallet/market/token/dynamic/info",
            params={"chainId": chain_id, "contractAddress": contract},
            headers=common_headers,
        )
        dynamic_resp.raise_for_status()
        dynamic_json = dynamic_resp.json()

        signal_resp = client.post(
            f"{base}/bapi/defi/v1/public/wallet-direct/buw/wallet/web/signal/smart-money",
            json={"smartSignalType": "", "page": 1, "pageSize": 100, "chainId": chain_id},
            headers={**common_headers, "Content-Type": "application/json"},
        )
        signal_resp.raise_for_status()
        signal_json = signal_resp.json()
        signal_items = signal_json.get("data") or []
        signal_matches = _matching_signal_items(signal_items, symbol, contract)

        audit_resp = client.post(
            f"{base}/bapi/defi/v1/public/wallet-direct/security/token/audit",
            json={"binanceChainId": chain_id, "contractAddress": contract, "requestId": str(uuid4())},
            headers={
                "Content-Type": "application/json",
                "Accept-Encoding": "identity",
                "User-Agent": "binance-web3/1.4 (Skill)",
                "source": "agent",
            },
        )
        audit_resp.raise_for_status()
        audit_json = audit_resp.json()

        # First live path: use unified rank defaults as general context.
        market_rank_resp = client.post(
            f"{base}/bapi/defi/v1/public/wallet-direct/buw/wallet/market/token/pulse/unified/rank/list",
            json={"rankType": 10, "chainId": chain_id, "period": 50, "sortBy": 70, "orderAsc": False, "page": 1, "size": 20},
            headers={"Content-Type": "application/json", **common_headers},
        )
        market_rank_resp.raise_for_status()
        market_rank_json = market_rank_resp.json()

    return {
        "query-token-info": {
            "search": search_items,
            "metadata": metadata_json.get("data", {}),
            "dynamic": dynamic_json.get("data", {}),
        },
        "crypto-market-rank": market_rank_json,
        "trading-signal": {"data": signal_matches},
        "query-token-audit": audit_json,
    }


def _require_httpx():
    try:
        import httpx  # type: ignore
    except ModuleNotFoundError as exc:
        raise HTTPException(status_code=500, detail="httpx is required for live bridge mode") from exc
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


def _skills_for(command: str) -> list[str] | None:
    mapping = {
        "token": TOKEN_SKILLS,
        "signal": SIGNAL_SKILLS,
        "wallet": WALLET_SKILLS,
        "watchtoday": WATCH_TODAY_SKILLS,
    }
    return mapping.get(command)
