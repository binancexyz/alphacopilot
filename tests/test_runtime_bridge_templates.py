from src.services.runtime_bridge_templates import (
    run_signal_flow,
    run_token_flow,
    run_wallet_flow,
    run_watchtoday_flow,
)


def test_run_token_flow():
    brief, payload = run_token_flow("BNB")
    assert brief.entity == "Token: BNB"
    assert payload.command == "token"


def test_run_signal_flow():
    brief, payload = run_signal_flow("DOGE")
    assert brief.entity == "Signal: DOGE"
    assert payload.command == "signal"


def test_run_wallet_flow():
    brief, payload = run_wallet_flow("0x123")
    assert brief.entity == "Wallet: 0x123"
    assert payload.command == "wallet"


def test_run_watchtoday_flow():
    brief, payload = run_watchtoday_flow()
    assert brief.entity == "Market Watch"
    assert payload.command == "watchtoday"


def test_run_token_flow_uses_raw_payload_when_provided():
    raw = {
        "query-token-info": {"symbol": "BNB", "price": 612.5, "liquidity": 125000000.0, "holders": 1850000},
        "crypto-market-rank": {"summary": "Large-cap token context.", "risks": ["Macro weakness"]},
        "trading-signal": {"status": "watch", "summary": "Momentum improving.", "risks": ["Need confirmation"]},
        "query-token-audit": {"flags": [], "risks": []},
    }
    brief, payload = run_token_flow("BNB", raw)
    assert brief.entity == "Token: BNB"
    assert "🧩 BNB" in brief.rendered or "🪙 BNB" in brief.rendered
    assert payload.raw == raw


def test_run_watchtoday_flow_uses_raw_payload_when_provided():
    raw = {"crypto-market-rank": {"top_narratives": ["AI"], "summary": "Opportunity exists.", "risks": ["Overheated names"]}}
    brief, payload = run_watchtoday_flow(raw)
    assert brief.entity == "Market Watch"
    assert "Watchtoday" in brief.rendered
    assert payload.raw == raw
