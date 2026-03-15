"""
Live API endpoint tests — verify REST API responses in live mode.

Gated behind LIVE_TESTS=1 and requires FastAPI + httpx test deps.
When run in mock mode these pass trivially (same as existing test_api.py).
The real value is running on the VPS with APP_MODE=live and BRIDGE_LIVE_ENABLED=true.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from src.api import app
from src.config import settings

client = TestClient(app)


def test_live_api_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "mode" in payload
    if settings.app_mode == "live":
        assert payload["mode"] == "live"
    assert "runtime" in payload or "config_warnings" in payload


def test_live_api_brief_bnb() -> None:
    response = client.get("/brief", params={"symbol": "BNB"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["rendered"], "rendered output must be non-empty"
    assert payload["mode"] in {"mock", "live"}


def test_live_api_brief_sol() -> None:
    response = client.get("/brief", params={"symbol": "SOL"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["rendered"], "rendered output must be non-empty"


def test_live_api_brief_deep_bnb() -> None:
    response = client.get("/brief", params={"symbol": "BNB", "deep": "true"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["command"] == "token"
    assert payload["rendered"], "rendered output must be non-empty"


def test_live_api_signal_bnb() -> None:
    response = client.get("/signal", params={"token": "BNB"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["command"] == "signal"
    assert payload["rendered"], "rendered output must be non-empty"


def test_live_api_signal_doge() -> None:
    response = client.get("/signal", params={"token": "DOGE"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["command"] == "signal"
    assert payload["rendered"], "rendered output must be non-empty"


def test_live_api_watchtoday() -> None:
    response = client.get("/watchtoday")
    assert response.status_code == 200
    payload = response.json()
    assert payload["command"] == "watchtoday"
    assert payload["rendered"], "rendered output must be non-empty"


def test_live_api_audit_bnb() -> None:
    response = client.get("/audit", params={"symbol": "BNB"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["command"] == "audit"
    assert payload["rendered"], "rendered output must be non-empty"


def test_live_api_alpha_bnb() -> None:
    response = client.get("/alpha", params={"symbol": "BNB"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["command"] == "alpha"
    assert payload["rendered"], "rendered output must be non-empty"


def test_live_api_futures_bnb() -> None:
    response = client.get("/futures", params={"symbol": "BNB"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["command"] == "futures"
    assert payload["rendered"], "rendered output must be non-empty"


def test_live_api_futures_eth() -> None:
    response = client.get("/futures", params={"symbol": "ETH"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["command"] == "futures"
    assert payload["rendered"], "rendered output must be non-empty"


def test_live_api_holdings() -> None:
    if not settings.binance_api_key:
        print("  SKIP  test_live_api_holdings (no BINANCE_API_KEY)")
        return
    response = client.get("/holdings")
    assert response.status_code == 200
    payload = response.json()
    assert payload["command"] == "holdings"
    assert payload["rendered"], "rendered output must be non-empty"
