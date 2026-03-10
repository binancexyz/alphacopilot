from __future__ import annotations

from datetime import datetime, UTC
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from src.services.binance_skill_mapping import SIGNAL_SKILLS, TOKEN_SKILLS, WALLET_SKILLS, WATCH_TODAY_SKILLS

app = FastAPI(title="Binance Alpha Copilot Live Bridge", version="0.1.0")


class BridgeMeta(BaseModel):
    source: str = "alpha-copilot-bridge-scaffold"
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
    return {"status": "ok", "service": "bridge", "mode": "scaffold"}


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

    return BridgeResponse(
        command=command_key,
        entity=entity,
        raw={},
        meta=BridgeMeta(
            generatedAt=datetime.now(UTC).isoformat(),
            skills=skills,
            notes=[
                "This is the bridge scaffold only.",
                "Implement Binance Skills invocation here and return raw payload bundles.",
            ],
        ),
    )


def _skills_for(command: str) -> list[str] | None:
    mapping = {
        "token": TOKEN_SKILLS,
        "signal": SIGNAL_SKILLS,
        "wallet": WALLET_SKILLS,
        "watchtoday": WATCH_TODAY_SKILLS,
    }
    return mapping.get(command)
