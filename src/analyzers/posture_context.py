from __future__ import annotations

from typing import Any

from src.analyzers.portfolio_analysis import get_portfolio_snapshot


def load_portfolio_posture() -> dict[str, Any] | None:
    try:
        return get_portfolio_snapshot()
    except Exception:
        return None


def posture_risk_note(snapshot: dict[str, Any] | None, symbol: str | None = None) -> str:
    if not snapshot:
        return ""
    stable_pct = float(snapshot.get("stable_pct") or 0)
    concentration = float(snapshot.get("concentration") or 0)
    posture = str(snapshot.get("posture") or "mixed")
    if concentration >= 70:
        return "Portfolio concentration is already high, so any new idea should clear a higher bar than usual."
    if stable_pct <= 20:
        return "Stablecoin dry powder is relatively thin, so new exposure should be treated more selectively."
    if stable_pct >= 55:
        return "Current posture is fairly defensive, so higher-beta ideas should earn their place instead of being chased by default."
    if posture == "mixed":
        return "Current posture is mixed, so new exposure should be judged on whether it truly improves the portfolio instead of just adding noise."
    return ""


def posture_watchtoday_note(snapshot: dict[str, Any] | None) -> str:
    if not snapshot:
        return ""
    stable_pct = float(snapshot.get("stable_pct") or 0)
    concentration = float(snapshot.get("concentration") or 0)
    if concentration >= 70:
        return "Your own posture is already concentrated, so today’s board matters more for filtering than for adding breadth blindly."
    if stable_pct >= 55:
        return "Your current posture still has meaningful stablecoin dry powder, so the board can be read selectively instead of defensively."
    if stable_pct <= 20:
        return "Your current posture is already quite deployed, so today’s board should be read with extra selectivity."
    return "Your current posture is mixed, so today’s board matters most for ranking what truly deserves additional exposure."
