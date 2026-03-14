from src.services.normalizers import (
    normalize_signal_context,
    normalize_token_context,
    normalize_wallet_context,
    normalize_watch_today_context,
)


def test_normalize_token_context():
    ctx = normalize_token_context({
        "symbol": "BNB",
        "price": "1.23",
        "holders": "12",
        "audit_flags": ["x"],
        "buy_sell_ratio": "0.63",
        "fdv": "2500000",
        "price_high_24h": "2.50",
        "price_low_24h": "1.10",
        "volume_5m": "1000",
        "volume_1h": "25000",
        "volume_4h": "125000",
        "pct_change_5m": "1.2",
        "pct_change_1h": "3.4",
        "pct_change_4h": "5.6",
        "tx_count_24h": "420",
        "kol_holders": "8",
        "kol_holding_pct": "4.5",
        "pro_holders": "3",
        "pro_holding_pct": "2.2",
    })
    assert ctx.symbol == "BNB"
    assert ctx.price == 1.23
    assert ctx.holders == 12
    assert ctx.audit_flags == ["x"]
    assert ctx.buy_sell_ratio == 0.63
    assert ctx.fdv == 2_500_000
    assert ctx.price_high_24h == 2.5
    assert ctx.price_low_24h == 1.1
    assert ctx.volume_5m == 1000
    assert ctx.volume_1h == 25_000
    assert ctx.volume_4h == 125_000
    assert ctx.pct_change_5m == 1.2
    assert ctx.pct_change_1h == 3.4
    assert ctx.pct_change_4h == 5.6
    assert ctx.tx_count_24h == 420
    assert ctx.kol_holders == 8
    assert ctx.kol_holding_pct == 4.5
    assert ctx.pro_holders == 3
    assert ctx.pro_holding_pct == 2.2


def test_normalize_wallet_context():
    ctx = normalize_wallet_context({"address": "0x123", "portfolio_value": "100", "top_holdings": [{"symbol": "BNB", "weight_pct": "40"}]})
    assert ctx.address == "0x123"
    assert ctx.portfolio_value == 100.0
    assert len(ctx.top_holdings) == 1
    assert ctx.top_holdings[0].symbol == "BNB"


def test_normalize_watch_today_context():
    ctx = normalize_watch_today_context({
        "top_narratives": ["AI"],
        "futures_sentiment": ["BTC funding +0.02% (bearish)"],
        "top_traders": ["0x1234…5678 — PnL $50K"],
    })
    assert ctx.top_narratives == ["AI"]
    assert ctx.futures_sentiment == ["BTC funding +0.02% (bearish)"]
    assert ctx.top_traders == ["0x1234…5678 — PnL $50K"]


def test_normalize_signal_context():
    ctx = normalize_signal_context({"token": "DOGE", "signal_status": "watch", "exit_rate": "78"})
    assert ctx.token == "DOGE"
    assert ctx.signal_status == "watch"
    assert ctx.exit_rate == 78.0
