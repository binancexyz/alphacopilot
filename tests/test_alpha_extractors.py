from __future__ import annotations

from src.services.live_extractors import extract_alpha_context


def test_extract_alpha_context_alpha_listed():
    raw = {
        "alpha": {
            "is_alpha_listed": True,
            "token_list": [{"symbol": "BNB"}],
            "ticker": {
                "lastPrice": "600.5",
                "volume": "12345",
                "priceChangePercent": "2.3",
                "highPrice": "610",
                "lowPrice": "590",
            },
        },
        "query-token-info": {
            "metadata": {"symbol": "BNB", "name": "BNB"},
            "search": [{"symbol": "BNB", "name": "BNB"}],
        },
        "query-token-audit": {},
        "spot": {"lastPrice": "601.0", "volume": "99999"},
    }
    ctx = extract_alpha_context(raw, "BNB")
    assert ctx["symbol"] == "BNB"
    assert ctx["is_alpha_listed"] is True
    assert ctx["alpha_price"] == 600.5
    assert ctx["alpha_volume_24h"] == 12345.0
    assert ctx["cex_price"] == 601.0
    assert ctx["audit_gate"] in ("ALLOW", "WARN")


def test_extract_alpha_context_not_alpha():
    raw = {
        "alpha": {
            "is_alpha_listed": False,
            "token_list": [],
        },
        "query-token-info": {
            "metadata": {"symbol": "DOGE", "name": "Dogecoin"},
        },
        "query-token-audit": {},
    }
    ctx = extract_alpha_context(raw, "DOGE")
    assert ctx["is_alpha_listed"] is False
    assert ctx["alpha_price"] == 0.0
    assert ctx["symbol"] == "DOGE"


def test_extract_alpha_context_empty_raw():
    ctx = extract_alpha_context({}, "XYZ")
    assert ctx["symbol"] == "XYZ"
    assert ctx["is_alpha_listed"] is False
    assert ctx["alpha_price"] == 0.0
    assert ctx["audit_gate"] in ("ALLOW", "WARN")
