from fastapi.testclient import TestClient

from src.bridge_api import app

client = TestClient(app)


def test_bridge_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "bridge"


def test_bridge_runtime_token_contract():
    response = client.get("/runtime", params={"command": "token", "entity": "BNB"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["command"] == "token"
    assert "query-token-info" in payload["meta"]["skills"]
    assert payload["raw"] == {}


def test_bridge_runtime_requires_entity_for_token():
    response = client.get("/runtime", params={"command": "token"})
    assert response.status_code == 400
