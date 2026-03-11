from fastapi.testclient import TestClient

from src.api import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "mode" in response.json()


def test_health_payload_shape():
    response = client.get("/health")
    payload = response.json()
    assert isinstance(payload, dict)
    assert "status" in payload
    assert "mode" in payload


def test_runtime_report_endpoint():
    response = client.get("/runtime/report")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "runtime" in payload


def test_token_endpoint():
    response = client.get("/brief/token", params={"symbol": "BNB"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["command"] == "token"
    assert payload["entity"] == "BNB"
    assert payload["mode"] in {"mock", "live"}
    assert payload["runtime_state"] in {"mock", "live_ok", "live_degraded", None}
    assert "Token: BNB" in payload["rendered"]


def test_watchtoday_endpoint():
    response = client.get("/brief/watchtoday")
    assert response.status_code == 200
    payload = response.json()
    assert payload["command"] == "watchtoday"
    assert payload["mode"] in {"mock", "live"}
    assert payload["runtime_state"] in {"mock", "live_ok", "live_degraded", None}
    assert "Market Watch" in payload["rendered"]


def test_wallet_endpoint_rejects_bad_address():
    response = client.get("/brief/wallet", params={"address": "not-a-wallet"})
    assert response.status_code == 400
