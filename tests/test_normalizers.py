from src.services.normalizers import (
    normalize_signal_context,
    normalize_token_context,
    normalize_wallet_context,
    normalize_watch_today_context,
)


def test_normalize_token_context():
    ctx = normalize_token_context({"symbol": "BNB", "price": 1.23, "audit_flags": ["x"]})
    assert ctx.symbol == "BNB"
    assert ctx.price == 1.23
    assert ctx.audit_flags == ["x"]


def test_normalize_wallet_context():
    ctx = normalize_wallet_context({"address": "0x123", "top_holdings": [{"symbol": "BNB", "weight_pct": 40}]})
    assert ctx.address == "0x123"
    assert len(ctx.top_holdings) == 1
    assert ctx.top_holdings[0].symbol == "BNB"


def test_normalize_watch_today_context():
    ctx = normalize_watch_today_context({"top_narratives": ["AI"]})
    assert ctx.top_narratives == ["AI"]


def test_normalize_signal_context():
    ctx = normalize_signal_context({"token": "DOGE", "signal_status": "watch"})
    assert ctx.token == "DOGE"
    assert ctx.signal_status == "watch"
