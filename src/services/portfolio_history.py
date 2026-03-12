from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

HISTORY_PATH = Path(__file__).resolve().parents[2] / "tmp" / "portfolio_history.json"
MAX_HISTORY = 30


def load_history() -> list[dict[str, Any]]:
    if not HISTORY_PATH.exists():
        return []
    try:
        payload = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []
    if not isinstance(payload, list):
        return []
    return [item for item in payload if isinstance(item, dict)]


def latest_snapshot() -> dict[str, Any] | None:
    history = load_history()
    return history[-1] if history else None


def _json_safe(value: Any) -> Any:
    if is_dataclass(value):
        return {k: _json_safe(v) for k, v in asdict(value).items()}
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(v) for v in value]
    return value


def append_snapshot(snapshot: dict[str, Any]) -> None:
    history = load_history()
    history.append({
        "saved_at": datetime.now(UTC).isoformat(),
        **_json_safe(snapshot),
    })
    trimmed = history[-MAX_HISTORY:]
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_PATH.write_text(json.dumps(trimmed, indent=2), encoding="utf-8")


def describe_delta(previous: dict[str, Any] | None, current: dict[str, Any]) -> tuple[str, list[str]]:
    if not previous:
        return "", []

    changes: list[str] = []
    total_prev = float(previous.get("total_value") or 0)
    total_cur = float(current.get("total_value") or 0)
    stable_prev = float(previous.get("stable_pct") or 0)
    stable_cur = float(current.get("stable_pct") or 0)
    conc_prev = float(previous.get("concentration") or 0)
    conc_cur = float(current.get("concentration") or 0)

    total_delta = total_cur - total_prev
    stable_delta = stable_cur - stable_prev
    conc_delta = conc_cur - conc_prev

    if abs(total_delta) >= 10:
        direction = "up" if total_delta > 0 else "down"
        changes.append(f"Estimated visible value is {direction} ${abs(total_delta):,.2f} versus the last saved snapshot.")

    prev_assets = {str(item.get('asset')): float(item.get('usd_value') or 0) for item in previous.get('priced_assets', []) if isinstance(item, dict)}
    cur_assets = {str(item.get('asset')): float(item.get('usd_value') or 0) for item in current.get('priced_assets', []) if isinstance(item, dict)}
    new_assets = [asset for asset in cur_assets if asset not in prev_assets]
    removed_assets = [asset for asset in prev_assets if asset not in cur_assets]
    if new_assets:
        changes.append(f"New priced assets since the last snapshot: {', '.join(new_assets[:3])}.")
    if removed_assets:
        changes.append(f"Assets no longer priced in the snapshot: {', '.join(removed_assets[:3])}.")
    if abs(stable_delta) >= 2:
        direction = "higher" if stable_delta > 0 else "lower"
        changes.append(f"Stablecoin share is {direction} by {abs(stable_delta):.1f} points.")
    if abs(conc_delta) >= 2:
        direction = "higher" if conc_delta > 0 else "lower"
        changes.append(f"Top concentration is {direction} by {abs(conc_delta):.1f} points.")

    summary = " ".join(changes[:2])
    return summary, changes[:3]
