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


def earlier_snapshot(steps_back: int = 3) -> dict[str, Any] | None:
    history = load_history()
    if len(history) <= steps_back:
        return None
    return history[-(steps_back + 1)]


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

    shared = []
    for asset, cur_value in cur_assets.items():
        if asset in prev_assets:
            delta = cur_value - prev_assets[asset]
            if abs(delta) >= 10:
                shared.append((asset, delta))
    if shared:
        shared.sort(key=lambda item: item[1], reverse=True)
        biggest_up = shared[0]
        biggest_down = min(shared, key=lambda item: item[1])
        if biggest_up[1] > 0:
            changes.append(f"Biggest increase: {biggest_up[0]} +${biggest_up[1]:,.2f}.")
        if biggest_down[1] < 0:
            changes.append(f"Biggest decrease: {biggest_down[0]} -${abs(biggest_down[1]):,.2f}.")

    posture_shift = []
    if abs(stable_delta) >= 2:
        direction = "more defensive" if stable_delta > 0 else "more deployed"
        posture_shift.append(f"posture looks {direction} by {abs(stable_delta):.1f} stable-share points")
    if abs(conc_delta) >= 2:
        direction = "more concentrated" if conc_delta > 0 else "less concentrated"
        posture_shift.append(f"top exposure is {direction} by {abs(conc_delta):.1f} points")
    if posture_shift:
        changes.append(f"Posture drift: {'; '.join(posture_shift)}.")

    summary = " ".join(changes[:2])
    return summary, changes[:5]


def describe_trend(reference: dict[str, Any] | None, current: dict[str, Any]) -> str:
    if not reference:
        return ""
    total_prev = float(reference.get("total_value") or 0)
    total_cur = float(current.get("total_value") or 0)
    stable_prev = float(reference.get("stable_pct") or 0)
    stable_cur = float(current.get("stable_pct") or 0)
    conc_prev = float(reference.get("concentration") or 0)
    conc_cur = float(current.get("concentration") or 0)

    trend_bits: list[str] = []
    total_delta = total_cur - total_prev
    if abs(total_delta) >= 25:
        direction = "up" if total_delta > 0 else "down"
        trend_bits.append(f"visible value is {direction} ${abs(total_delta):,.0f} versus the older local trend")
    stable_delta = stable_cur - stable_prev
    if abs(stable_delta) >= 3:
        direction = "more defensive" if stable_delta > 0 else "more deployed"
        trend_bits.append(f"posture looks {direction} over the short local trend")
    conc_delta = conc_cur - conc_prev
    if abs(conc_delta) >= 3:
        direction = "more concentrated" if conc_delta > 0 else "less concentrated"
        trend_bits.append(f"top concentration is {direction} over the short local trend")
    return "; ".join(trend_bits[:2]).strip()
