from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.services.fallbacks import missing_context_warning
from src.services.live_extractors import (
    extract_audit_context,
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

    def get_token_context(self, symbol: str) -> NormalizedDict:
        raw = self._load_payload("token", symbol)
        context = extract_token_context(raw, symbol)
        return self._apply_fallbacks("token", context)

    def get_wallet_context(self, address: str) -> NormalizedDict:
        raw = self._load_payload("wallet", address)
        context = extract_wallet_context(raw, address)
        return self._apply_fallbacks("wallet", context)

    def get_watch_today_context(self) -> NormalizedDict:
        raw = self._load_payload("watchtoday")
        context = extract_watch_today_context(raw)
        return self._apply_fallbacks("watchtoday", context)

    def get_signal_context(self, token: str) -> NormalizedDict:
        raw = self._load_payload("signal", token)
        context = extract_signal_context(raw, token)
        return self._apply_fallbacks("signal", context)

    def get_audit_context(self, symbol: str) -> NormalizedDict:
        raw = self._load_payload("audit", symbol)
        context = extract_audit_context(raw, symbol)
        return self._apply_fallbacks("audit", context)

    def _load_payload(self, command: str, entity: str = "") -> dict[str, Any]:
        if not self.base_url:
            raise RuntimeError(
                "APP_MODE=live requires BINANCE_SKILLS_BASE_URL. "
                "Use an HTTP adapter URL or file:///path/to/payload-dir."
            )

        if self.base_url.startswith("file://"):
            return self._load_from_directory(command, entity)

        return self._load_from_http(command, entity)

    def _load_from_directory(self, command: str, entity: str = "") -> dict[str, Any]:
        base_path = Path(self.base_url.removeprefix("file://")).expanduser()
        candidates = self._candidate_paths(base_path, command, entity)
        for path in candidates:
            if path.exists() and path.is_file():
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
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
        with httpx.Client(timeout=20.0, follow_redirects=True) as client:
            response = client.get(endpoint, params=params, headers=headers)
            response.raise_for_status()
            payload = response.json()

        if not isinstance(payload, dict):
            raise RuntimeError(f"Live adapter returned non-object JSON for {command!r}: {type(payload).__name__}")

        if "raw" in payload and isinstance(payload["raw"], dict):
            return payload["raw"]
        return payload

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
        risks = list(context.get("major_risks", []))
        if command == "audit":
            has_live_audit = bool(context.get("audit_summary")) and str(context.get("audit_gate", "WARN")).upper() in {"ALLOW", "WARN", "BLOCK"}
            if not risks and not has_live_audit:
                risks.append(missing_context_warning(command))
            context["major_risks"] = risks
            return context
        if not risks:
            risks.append(missing_context_warning(command))
        context["major_risks"] = risks
        return context
