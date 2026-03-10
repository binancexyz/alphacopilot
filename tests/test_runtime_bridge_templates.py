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
