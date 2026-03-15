from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SNAPSHOT_DIR = Path(__file__).resolve().parents[2] / "tmp" / "snapshots"
MAX_SNAPSHOTS_PER_KEY = 10


def _snapshot_path(command: str, entity: str = "") -> Path:
    safe_entity = entity.upper().replace("/", "_").replace("\\", "_") if entity else "_global"
    return SNAPSHOT_DIR / f"{command}_{safe_entity}.json"


def _load_snapshots(command: str, entity: str = "") -> list[dict[str, Any]]:
    path = _snapshot_path(command, entity)
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if not isinstance(payload, list):
        return []
    return [item for item in payload if isinstance(item, dict)]


def save_snapshot(command: str, entity: str, data: dict[str, Any]) -> None:
    snapshots = _load_snapshots(command, entity)
    snapshots.append({
        "saved_at": datetime.now(UTC).isoformat(),
        **data,
    })
    trimmed = snapshots[-MAX_SNAPSHOTS_PER_KEY:]
    path = _snapshot_path(command, entity)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(trimmed, indent=2, default=str), encoding="utf-8")


def latest_snapshot(command: str, entity: str = "") -> dict[str, Any] | None:
    snapshots = _load_snapshots(command, entity)
    return snapshots[-1] if snapshots else None


def describe_snapshot_delta(command: str, entity: str, current: dict[str, Any]) -> tuple[str, list[str]]:
    previous = latest_snapshot(command, entity)
    if not previous:
        return "", []

    changes: list[str] = []
    watch: list[str] = []

    if command == "brief":
        prev_quality = str(previous.get("signal_quality") or "")
        cur_quality = str(current.get("signal_quality") or "")
        if prev_quality and cur_quality and prev_quality != cur_quality:
            changes.append(f"Signal quality shifted from {prev_quality} to {cur_quality}.")

        prev_verdict = str(previous.get("quick_verdict") or "")
        cur_verdict = str(current.get("quick_verdict") or "")
        if prev_verdict and cur_verdict and prev_verdict != cur_verdict:
            changes.append("Verdict changed since last check.")

        prev_conviction = str(previous.get("conviction") or "")
        cur_conviction = str(current.get("conviction") or "")
        if prev_conviction and cur_conviction and prev_conviction != cur_conviction:
            changes.append(f"Conviction moved from {prev_conviction} to {cur_conviction}.")
            watch.append("whether conviction direction holds or reverses in the next cycle")

    elif command == "signal":
        prev_state = str(previous.get("state") or "")
        cur_state = str(current.get("state") or "")
        if prev_state and cur_state and prev_state != cur_state:
            changes.append(f"Signal state shifted from {prev_state} to {cur_state}.")
            if cur_state in ("late", "stale", "fragile") and prev_state in ("active", "early"):
                watch.append("signal is degrading — consider reducing exposure or tightening stops")

        prev_quality = str(previous.get("signal_quality") or "")
        cur_quality = str(current.get("signal_quality") or "")
        if prev_quality and cur_quality and prev_quality != cur_quality:
            changes.append(f"Quality shifted from {prev_quality} to {cur_quality}.")

    elif command == "watchtoday":
        prev_signals = int(previous.get("signal_count") or 0)
        cur_signals = int(current.get("signal_count") or 0)
        if prev_signals is not None and cur_signals is not None:
            delta = cur_signals - prev_signals
            if abs(delta) >= 1:
                direction = "more" if delta > 0 else "fewer"
                changes.append(f"{abs(delta)} {direction} active signal areas than last check.")

        prev_regime = str(previous.get("market_regime") or "")
        cur_regime = str(current.get("market_regime") or "")
        if prev_regime and cur_regime and prev_regime != cur_regime:
            changes.append(f"Market regime shifted from {prev_regime} to {cur_regime}.")
            watch.append("whether the regime shift is durable or just a reaction to a single candle")

    summary = " ".join(changes[:3])
    return summary, watch[:2]
