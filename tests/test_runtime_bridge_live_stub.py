from src.services.runtime_bridge_live_stub import signal_from_raw, token_from_raw, wallet_from_raw, watchtoday_from_raw
from src.services.live_payload_examples import TOKEN_RAW_EXAMPLE


def test_token_from_raw_returns_text():
    out = token_from_raw("BNB", TOKEN_RAW_EXAMPLE)
    assert "BNB" in out
    assert len(out) > 50


def test_signal_from_raw_returns_text():
    raw = {
        "trading-signal": {"status": "watch", "summary": "Momentum improving.", "risks": ["Fragile setup"]},
        "query-token-audit": {"flags": [], "risks": []},
    }
    out = signal_from_raw("DOGE", raw)
    assert "DOGE" in out
    assert len(out) > 50


def test_wallet_from_raw_returns_text():
    raw = {"query-address-info": {"address": "0x123", "top_concentration_pct": 61.0, "major_risks": ["Low diversification"]}}
    out = wallet_from_raw("0x123", raw)
    assert "0x123" in out
    assert len(out) > 50


def test_watchtoday_from_raw_returns_text():
    raw = {"crypto-market-rank": {"top_narratives": ["AI"], "summary": "Opportunity exists.", "risks": ["Overheated names"]}}
    out = watchtoday_from_raw(raw)
    assert "Watch" in out or "watch" in out.lower()
    assert len(out) > 50
