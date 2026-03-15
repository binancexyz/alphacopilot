from __future__ import annotations

from typing import Any

from datetime import datetime, UTC

from src.config import settings
from src.models.schemas import AnalysisBrief, RiskTag
from src.services.live_service import LiveMarketDataService


def live_service() -> LiveMarketDataService:
    return LiveMarketDataService(
        base_url=settings.binance_skills_base_url,
        bridge_api_key=settings.bridge_api_key or settings.api_auth_key,
        bridge_api_header=settings.bridge_api_header,
    )


def build_runtime_meta(command: str, entity: str = "", *, health: dict[str, Any] | None = None) -> dict[str, Any]:
    if settings.app_mode != "live":
        return {
            "mode": settings.app_mode,
            "state": "mock",
            "warning": "Running in mock mode; outputs are scaffold/demo quality, not live market calls.",
            "trust_label": "🔴 Mock / not live",
            "generated_at": datetime.now(UTC).isoformat(),
        }

    if health is None:
        health = live_service().healthcheck()
    last_event = health.get("last_event") or {}
    state = "live_ok" if health.get("healthcheck") == "ok" else "live_degraded"
    warning = None if state == "live_ok" else str(last_event.get("detail") or "Live runtime is degraded.")
    trust_label = "✅ Live now" if state == "live_ok" else "🟡 Partial live / degraded"
    return {
        "mode": settings.app_mode,
        "state": state,
        "warning": warning,
        "trust_label": trust_label,
        "bridge_mode": health.get("bridge_mode"),
        "last_event": last_event,
        "generated_at": datetime.now(UTC).isoformat(),
        "command": command,
        "entity": entity,
    }


def apply_runtime_meta(brief: AnalysisBrief, runtime_meta: dict[str, Any]) -> AnalysisBrief:
    brief.runtime_state = str(runtime_meta.get("state") or "") or None
    brief.runtime_warning = runtime_meta.get("warning")
    trust_label = runtime_meta.get("trust_label")
    generated_at = str(runtime_meta.get("generated_at") or "").replace("+00:00", "Z")
    if trust_label and not any(tag.name == "Live Trust" for tag in brief.risk_tags):
        brief.risk_tags.insert(0, RiskTag(name="Live Trust", level=str(trust_label), note=generated_at))
    if brief.runtime_warning and brief.runtime_warning not in brief.top_risks:
        brief.top_risks.insert(0, str(brief.runtime_warning))
    return brief
