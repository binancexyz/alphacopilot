from __future__ import annotations

from typing import Any

from src.config import settings
from src.models.schemas import AnalysisBrief
from src.services.live_service import LiveMarketDataService


def build_runtime_meta(command: str, entity: str = "") -> dict[str, Any]:
    if settings.app_mode != "live":
        return {
            "mode": settings.app_mode,
            "state": "mock",
            "warning": "Running in mock mode; outputs are scaffold/demo quality, not live market calls.",
        }

    service = LiveMarketDataService(
        base_url=settings.binance_skills_base_url,
        api_key=settings.binance_api_key,
        api_secret=settings.binance_api_secret,
    )
    health = service.healthcheck()
    last_event = health.get("last_event") or {}
    state = "live_ok" if health.get("healthcheck") == "ok" else "live_degraded"
    warning = None if state == "live_ok" else str(last_event.get("detail") or "Live runtime is degraded.")
    return {
        "mode": settings.app_mode,
        "state": state,
        "warning": warning,
        "bridge_mode": health.get("bridge_mode"),
        "last_event": last_event,
        "command": command,
        "entity": entity,
    }


def apply_runtime_meta(brief: AnalysisBrief, runtime_meta: dict[str, Any]) -> AnalysisBrief:
    brief.runtime_state = str(runtime_meta.get("state") or "") or None
    brief.runtime_warning = runtime_meta.get("warning")
    if brief.runtime_warning and brief.runtime_warning not in brief.top_risks:
        brief.top_risks.insert(0, str(brief.runtime_warning))
    return brief
