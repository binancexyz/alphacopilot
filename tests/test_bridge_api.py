from src.bridge_api import _first_matching_token, app
from src.config import settings


def test_bridge_health():
    from fastapi.testclient import TestClient

    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "bridge"
    assert "guard" in response.json()


def test_bridge_runtime_token_contract():
    from fastapi.testclient import TestClient

    client = TestClient(app)
    response = client.get("/runtime", params={"command": "token", "entity": "BNB"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["command"] == "token"
    assert "query-token-info" in payload["meta"]["skills"]


def test_bridge_runtime_requires_entity_for_token():
    from fastapi.testclient import TestClient

    client = TestClient(app)
    response = client.get("/runtime", params={"command": "token"})
    assert response.status_code == 400


def test_bridge_runtime_rejects_wrong_bridge_key():
    from fastapi.testclient import TestClient

    old_key = settings.bridge_api_key
    old_header = settings.bridge_api_header
    settings.bridge_api_key = "bridge-secret"
    settings.bridge_api_header = "X-Bridge-Key"
    try:
        client = TestClient(app)
        response = client.get(
            "/runtime",
            params={"command": "token", "entity": "BNB"},
            headers={"X-Bridge-Key": "wrong"},
        )
        assert response.status_code == 401
    finally:
        settings.bridge_api_key = old_key
        settings.bridge_api_header = old_header


def test_first_matching_token_prefers_exact_symbol():
    items = [{"symbol": "DOGE"}, {"symbol": "BNB"}]
    out = _first_matching_token(items, "BNB")
    assert out == {"symbol": "BNB"}
