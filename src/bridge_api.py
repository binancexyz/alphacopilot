from __future__ import annotations

from datetime import datetime, UTC
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from src.config import settings
from src.services.binance_skill_bridge import _first_matching_token, fetch_live_bundle
from src.services.binance_skill_mapping import COMMAND_SKILL_MAP

app = FastAPI(title="Bibipilot Live Bridge", version="0.2.0")


class BridgeMeta(BaseModel):
    source: str = "bibipilot-bridge"
    generatedAt: str
    skills: list[str] = Field(default_factory=list)
    status: str = "not-implemented"
    notes: list[str] = Field(default_factory=list)
    failedSkills: list[str] = Field(default_factory=list)
    errors: dict[str, str] = Field(default_factory=dict)
    skillRefs: dict[str, dict[str, Any]] = Field(default_factory=dict)


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
    command: str = Query(..., description="token|signal|wallet|watchtoday|audit|meme|portfolio"),
    entity: str = Query("", description="symbol or address when relevant"),
) -> BridgeResponse:
    command_key = command.strip().lower()
    skills = _skills_for(command_key)
    if skills is None:
        raise HTTPException(status_code=400, detail=f"Unsupported command: {command}")

    if command_key in {"token", "signal", "audit", "meme", "futures"} and not entity:
        raise HTTPException(status_code=400, detail=f"command={command_key} requires entity")
    if command_key == "wallet" and not entity:
        raise HTTPException(status_code=400, detail="command=wallet requires entity")

    if settings.bridge_live_enabled:
        bundle = fetch_live_bundle(command_key, entity)
        meta_payload = dict(bundle.meta)
        meta_payload["generatedAt"] = datetime.now(UTC).isoformat()
        return BridgeResponse(
            command=command_key,
            entity=entity,
            raw=bundle.raw,
            meta=BridgeMeta(**meta_payload),
        )

    return BridgeResponse(
        command=command_key,
        entity=entity,
        raw={},
        meta=BridgeMeta(
            generatedAt=datetime.now(UTC).isoformat(),
            skills=skills,
            skillRefs={},
            notes=[
                "This is the bridge scaffold only.",
                "Enable BRIDGE_LIVE_ENABLED=true to execute documented Binance skill calls.",
            ],
        ),
    )


def _skills_for(command: str) -> list[str] | None:
    return COMMAND_SKILL_MAP.get(command)
