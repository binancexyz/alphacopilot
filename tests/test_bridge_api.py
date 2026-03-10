from src.bridge_api import _first_matching_token, app


def test_bridge_health():
    from fastapi.testclient import TestClient

    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "bridge"


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


def test_first_matching_token_prefers_exact_symbol():
    items = [{"symbol": "DOGE"}, {"symbol": "BNB"}]
    out = _first_matching_token(items, "BNB")
    assert out == {"symbol": "BNB"}
