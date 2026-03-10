from fastapi.testclient import TestClient

from src.api import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_token_endpoint():
    response = client.get("/brief/token", params={"symbol": "BNB"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["command"] == "token"
    assert payload["entity"] == "BNB"
    assert "Token: BNB" in payload["rendered"]


def test_watchtoday_endpoint():
    response = client.get("/brief/watchtoday")
    assert response.status_code == 200
    payload = response.json()
    assert payload["command"] == "watchtoday"
    assert "Market Watch" in payload["rendered"]


def test_wallet_endpoint_rejects_bad_address():
    response = client.get("/brief/wallet", params={"address": "not-a-wallet"})
    assert response.status_code == 400
