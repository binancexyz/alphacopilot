from __future__ import annotations

import json
from pathlib import Path
from time import sleep, time
from typing import Any

from src.config import settings
from src.services.fallbacks import missing_context_warning
from src.services.live_extractors import (
    extract_alpha_context,
    extract_audit_context,
    extract_futures_context,
    extract_meme_context,
    extract_signal_context,
    extract_token_context,
    extract_wallet_context,
    extract_watch_today_context,
)
from src.services.types import NormalizedDict


class LiveMarketDataService:
    """
    Runtime-facing adapter for live mode.

    Supported input paths:
    1. HTTP bridge: point ``base_url`` at a small adapter that returns raw skill outputs.
    2. File bridge: point ``base_url`` at a directory using ``file:///absolute/path`` and
       provide JSON payload files named after the command/entity.

    Expected raw payload shapes match ``src/services/live_extractors.py``.
    """

    def __init__(self, base_url: str, api_key: str = "", api_secret: str = "") -> None:
        self.base_url = (base_url or "").strip()
        self.api_key = api_key
        self.api_secret = api_secret
        self._last_runtime_event: dict[str, Any] = {
            "status": "idle",
            "command": "",
            "entity": "",
            "detail": "No live requests attempted yet.",
            "timestamp": 0.0,
        }

    def get_token_context(self, symbol: str) -> NormalizedDict:
        try:
            raw = self._load_payload("token", symbol)
            context = extract_token_context(raw, symbol)
            return self._apply_fallbacks("token", context)
        except Exception as exc:
            return self._apply_fallbacks("token", self._bridge_unavailable_context("token", symbol, str(exc)))

    def get_wallet_context(self, address: str) -> NormalizedDict:
        try:
            raw = self._load_payload("wallet", address)
            context = extract_wallet_context(raw, address)
            return self._apply_fallbacks("wallet", context)
        except Exception as exc:
            return self._apply_fallbacks("wallet", self._bridge_unavailable_context("wallet", address, str(exc)))

    def get_watch_today_context(self) -> NormalizedDict:
        try:
            raw = self._load_payload("watchtoday")
            context = extract_watch_today_context(raw)
            return self._apply_fallbacks("watchtoday", context)
        except Exception as exc:
            return self._apply_fallbacks("watchtoday", self._bridge_unavailable_context("watchtoday", "", str(exc)))

    def get_signal_context(self, token: str) -> NormalizedDict:
        try:
            raw = self._load_payload("signal", token)
            context = extract_signal_context(raw, token)
            return self._apply_fallbacks("signal", context)
        except Exception as exc:
            return self._apply_fallbacks("signal", self._bridge_unavailable_context("signal", token, str(exc)))

    def get_audit_context(self, symbol: str) -> NormalizedDict:
        try:
            raw = self._load_payload("audit", symbol)
            context = extract_audit_context(raw, symbol)
            return self._apply_fallbacks("audit", context)
        except Exception as exc:
            return self._apply_fallbacks("audit", self._bridge_unavailable_context("audit", symbol, str(exc)))

    def get_meme_context(self, symbol: str) -> NormalizedDict:
        try:
            raw = self._load_payload("meme", symbol)
            context = extract_meme_context(raw, symbol)
            return self._apply_fallbacks("meme", context)
        except Exception as exc:
            return self._apply_fallbacks("meme", self._bridge_unavailable_context("meme", symbol, str(exc)))

    def get_alpha_context(self, symbol: str) -> NormalizedDict:
        try:
            raw = self._load_payload("alpha", symbol)
            context = extract_alpha_context(raw, symbol)
            return self._apply_fallbacks("alpha", context)
        except Exception as exc:
            return self._apply_fallbacks("alpha", self._bridge_unavailable_context("alpha", symbol, str(exc)))

    def get_futures_context(self, symbol: str) -> NormalizedDict:
        try:
            raw = self._load_payload("futures", symbol)
            context = extract_futures_context(raw, symbol)
            return self._apply_fallbacks("futures", context)
        except Exception as exc:
            return self._apply_fallbacks("futures", self._bridge_unavailable_context("futures", symbol, str(exc)))

    def get_portfolio_context(self) -> NormalizedDict:
        try:
            raw = self._load_payload("portfolio")
            # We skip 'extractors' for portfolio because it operates natively on the raw dict in 'portfolio_analysis.py'
            return self._apply_fallbacks("portfolio", raw)
        except Exception as exc:
            return self._apply_fallbacks("portfolio", self._bridge_unavailable_context("portfolio", "account", str(exc)))

    def _load_payload(self, command: str, entity: str = "") -> dict[str, Any]:
        if not self.base_url:
            self._record_runtime_event("error", command, entity, "BINANCE_SKILLS_BASE_URL is not configured in live mode.")
            raise RuntimeError(
                "APP_MODE=live requires BINANCE_SKILLS_BASE_URL. "
                "Use an HTTP adapter URL or file:///path/to/payload-dir."
            )

        if self.base_url.startswith("file://"):
            payload = self._load_from_directory(command, entity)
            self._record_runtime_event("ok", command, entity, "Loaded live payload from file bridge.")
            return payload

        payload = self._load_from_http(command, entity)
        self._record_runtime_event("ok", command, entity, "Loaded live payload from HTTP bridge.")
        return payload

    def _load_from_directory(self, command: str, entity: str = "") -> dict[str, Any]:
        base_path = Path(self.base_url.removeprefix("file://")).expanduser().resolve()
        candidates = self._candidate_paths(base_path, command, entity)
        for path in candidates:
            resolved = path.resolve()
            if not resolved.is_relative_to(base_path):
                continue
            if resolved.exists() and resolved.is_file():
                with open(resolved, "r", encoding="utf-8") as f:
                    return self._unwrap_bridge_payload(json.load(f))
        raise FileNotFoundError(
            "No live payload file found for "
            f"command={command!r} entity={entity!r}. Checked: {', '.join(str(p) for p in candidates)}"
        )

    def _load_from_http(self, command: str, entity: str = "") -> dict[str, Any]:
        try:
            import httpx  # type: ignore
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "HTTP live mode requires the optional dependency 'httpx'. "
                "Install requirements.txt or use file:// live mode."
            ) from exc

        params = {"command": command}
        if entity:
            params["entity"] = entity

        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        if self.api_secret:
            headers["X-API-Secret"] = self.api_secret

        endpoint = self.base_url.rstrip("/")
        if not endpoint.startswith(("https://", "http://")):
            raise RuntimeError(f"Live bridge URL must use http or https scheme, got: {endpoint!r}")

        last_exc: Exception | None = None
        for attempt in range(max(1, settings.bridge_http_retries)):
            try:
                with httpx.Client(timeout=settings.bridge_http_timeout_seconds, follow_redirects=False) as client:
                    response = client.get(endpoint, params=params, headers=headers)
                    response.raise_for_status()
                    payload = response.json()
                break
            except Exception as exc:
                last_exc = exc
                if attempt < max(1, settings.bridge_http_retries) - 1:
                    sleep(0.4 * (attempt + 1))
                else:
                    raise RuntimeError(f"Live bridge request failed for command={command!r} entity={entity!r} at {endpoint}: {exc}") from exc

        if not isinstance(payload, dict):
            raise RuntimeError(f"Live adapter returned non-object JSON for {command!r}: {type(payload).__name__}")

        return self._unwrap_bridge_payload(payload)

    def _candidate_paths(self, base_path: Path, command: str, entity: str = "") -> list[Path]:
        slug = self._slug(entity)
        candidates: list[Path] = []
        if entity:
            candidates.extend(
                [
                    base_path / command / f"{slug}.json",
                    base_path / command / f"{entity}.json",
                    base_path / f"{command}-{slug}.json",
                    base_path / f"{command}-{entity}.json",
                ]
            )
        candidates.append(base_path / f"{command}.json")
        return candidates

    def _unwrap_bridge_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        if "raw" in payload and isinstance(payload["raw"], dict):
            raw = dict(payload["raw"])
            meta = payload.get("meta")
            if isinstance(meta, dict):
                raw["__bridge_meta__"] = meta
            return raw
        return payload

    @staticmethod
    def _slug(value: str) -> str:
        cleaned = []
        for ch in value.strip().lower():
            cleaned.append(ch if ch.isalnum() else "-")
        slug = "".join(cleaned).strip("-")
        while "--" in slug:
            slug = slug.replace("--", "-")
        return slug or "default"

    def _apply_fallbacks(self, command: str, context: dict[str, Any]) -> dict[str, Any]:
        context = dict(context)
        risks = self._unique_risks(context.get("major_risks", []))
        runtime_state = self._runtime_state_warning(command, context)
        if runtime_state and runtime_state not in risks:
            risks.insert(0, runtime_state)

        if command == "audit":
            has_live_audit = bool(context.get("audit_summary")) and str(context.get("audit_gate", "WARN")).upper() in {"ALLOW", "WARN", "BLOCK"}
            if not risks and not has_live_audit:
                risks.append(missing_context_warning(command))
            context["major_risks"] = self._unique_risks(risks)
            return context

        if not risks:
            risks.append(missing_context_warning(command))
        context["major_risks"] = self._unique_risks(risks)
        return context

    def _runtime_state_warning(self, command: str, context: dict[str, Any]) -> str:
        if context.get("runtime_state") == "bridge_unavailable":
            return str(context.get("runtime_warning") or f"Live bridge is unavailable for {command}; using degraded context.")
        if context.get("runtime_state") == "partial_live":
            return str(context.get("runtime_warning") or f"Live {command} payload is only partially populated right now.")
        if command == "token" and context.get("signal_status") == "unmatched":
            return "No matched live smart-money signal is visible on the current board, so this token read stays capped."
        if command == "signal" and context.get("signal_status") == "unmatched":
            return "No matched live smart-money signal is visible on the current board, so this signal read is watchlist-only."
        if command == "watchtoday":
            populated = sum(1 for key in ("trending_now", "smart_money_flow", "social_hype", "meme_watch", "top_narratives", "top_picks") if context.get(key))
            if populated <= 2:
                return "Today’s live board is only lightly populated, so treat the market view as partial rather than complete."
        if command == "wallet":
            if not context.get("top_holdings") and not context.get("holdings_count") and not context.get("portfolio_value"):
                return "Live wallet payload is too thin for a strong behavior read right now."
        if command == "meme":
            if str(context.get("lifecycle_stage", "unknown")).lower() == "unknown" and not context.get("smart_money_count"):
                return "Live meme context is thin right now, so lifecycle and participation reads stay provisional."
        return ""

    def _bridge_unavailable_context(self, command: str, entity: str, detail: str) -> dict[str, Any]:
        warning = f"Live bridge is unavailable for {command}; using degraded context."
        sanitized = self._sanitize_runtime_detail(detail)
        if command == "portfolio":
            return {
                "_raw": {},
                "runtime_state": "bridge_unavailable",
                "runtime_warning": warning,
                "major_risks": [warning, sanitized]
            }
        if command == "token":
            return {
                "symbol": entity or "UNKNOWN",
                "display_name": entity or "UNKNOWN",
                "runtime_state": "bridge_unavailable",
                "runtime_warning": warning,
                "major_risks": [warning, sanitized],
            }
        if command == "signal":
            return {
                "token": entity or "UNKNOWN",
                "signal_status": "unknown",
                "supporting_context": "Live signal bridge is currently unavailable.",
                "runtime_state": "bridge_unavailable",
                "runtime_warning": warning,
                "major_risks": [warning, sanitized],
            }
        if command == "audit":
            return {
                "symbol": entity or "UNKNOWN",
                "display_name": entity or "UNKNOWN",
                "audit_gate": "WARN",
                "blocked_reason": "Live audit bridge is unavailable.",
                "risk_level": "Medium",
                "audit_summary": "Live audit payload unavailable.",
                "runtime_state": "bridge_unavailable",
                "runtime_warning": warning,
                "major_risks": [warning, sanitized],
            }
        if command == "wallet":
            return {
                "address": entity,
                "follow_verdict": "Unknown",
                "style_read": "Live wallet bridge is unavailable.",
                "runtime_state": "bridge_unavailable",
                "runtime_warning": warning,
                "major_risks": [warning, sanitized],
            }
        if command == "meme":
            return {
                "symbol": entity or "UNKNOWN",
                "display_name": entity or "UNKNOWN",
                "audit_gate": "WARN",
                "lifecycle_stage": "unknown",
                "runtime_state": "bridge_unavailable",
                "runtime_warning": warning,
                "major_risks": [warning, sanitized],
            }
        return {
            "market_takeaway": "Live market board is temporarily unavailable.",
            "runtime_state": "bridge_unavailable",
            "runtime_warning": warning,
            "major_risks": [warning, sanitized],
        }

    def _sanitize_runtime_detail(self, detail: str) -> str:
        cleaned = " ".join(str(detail or "").split())
        if not cleaned:
            return "Runtime detail unavailable."
        lowered = cleaned.lower()
        if "404" in lowered or "not found" in lowered:
            return "Upstream live payload was not found for this request."
        if "timeout" in lowered:
            return "Upstream live request timed out before a stable payload arrived."
        if "connection" in lowered or "refused" in lowered:
            return "Could not reach the upstream live bridge."
        if len(cleaned) > 180:
            cleaned = cleaned[:177].rstrip() + "..."
        return f"Runtime detail: {cleaned}"

    def _record_runtime_event(self, status: str, command: str, entity: str, detail: str) -> None:
        self._last_runtime_event = {
            "status": status,
            "command": command,
            "entity": entity,
            "detail": self._sanitize_runtime_detail(detail) if status != "ok" else detail,
            "timestamp": time(),
        }

    def runtime_status(self) -> dict[str, Any]:
        mode = "file" if self.base_url.startswith("file://") else "http" if self.base_url else "unconfigured"
        return {
            "bridge_mode": mode,
            "base_url": self.base_url or "",
            "last_event": dict(self._last_runtime_event),
        }

    def healthcheck(self) -> dict[str, Any]:
        status = self.runtime_status()
        if not settings.bridge_healthcheck_enabled:
            status["healthcheck"] = "disabled"
            return status
        if not self.base_url:
            status["healthcheck"] = "unconfigured"
            return status
        try:
            self._load_payload("watchtoday")
            status = self.runtime_status()
            status["healthcheck"] = "ok"
            return status
        except Exception as exc:
            self._record_runtime_event("error", "watchtoday", "", str(exc))
            status = self.runtime_status()
            status["healthcheck"] = "error"
            return status

    def _unique_risks(self, risks: list[Any]) -> list[str]:
        out: list[str] = []
        for item in risks or []:
            text = str(item).strip()
            if text and text not in out:
                out.append(text)
        return out
