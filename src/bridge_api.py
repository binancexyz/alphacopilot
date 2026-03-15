from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, UTC
from typing import Any
import logging

from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response
from pydantic import BaseModel, Field

from src.config import config_errors, config_warnings, settings
from src.services.api_guard import bridge_guard_status, enforce_bridge_guard
from src.services.binance_skill_bridge import _first_matching_token, fetch_live_bundle
from src.services.binance_skill_mapping import COMMAND_SKILL_MAP
from src.version import __version__

logger = logging.getLogger("bibipilot.bridge")


@asynccontextmanager
async def lifespan(app: FastAPI):
    for warning in config_warnings():
        logger.warning("startup_config_warning warning=%s", warning)
    errors = config_errors("bridge")
    if errors:
        for error in errors:
            logger.error("startup_config_error error=%s", error)
        raise RuntimeError("Invalid production configuration: " + " | ".join(errors))
    yield


app = FastAPI(title="Bibipilot Live Bridge", version=__version__, lifespan=lifespan)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Content-Security-Policy"] = "default-src 'none'"
    return response


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
def health(_: None = Depends(enforce_bridge_guard)) -> dict[str, object]:
    return {
        "status": "ok",
        "service": "bridge",
        "mode": "live-enabled" if settings.bridge_live_enabled else "scaffold",
        "guard": bridge_guard_status(),
    }


@app.get("/runtime", response_model=BridgeResponse)
def runtime(
    _: None = Depends(enforce_bridge_guard),
    command: str = Query(..., description="token|signal|wallet|watchtoday|audit|meme|portfolio|alpha|futures"),
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
