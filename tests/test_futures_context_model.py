from src.models.context import FuturesContext
from src.services.normalizers import normalize_futures_context


def test_futures_context_dataclass():
    ctx = FuturesContext(
        symbol="BTC",
        funding_rate=0.001,
        open_interest=500_000_000,
        oi_change_pct_24h=5.0,
        liquidation_24h_long=10_000_000,
    )
    assert ctx.symbol == "BTC"
    assert ctx.funding_rate == 0.001
    assert ctx.oi_change_pct_24h == 5.0
    assert ctx.liquidation_24h_long == 10_000_000
    print("PASS test_futures_context_dataclass")


def test_normalize_futures_context():
    payload = {
        "symbol": "eth",
        "funding_rate": 0.0005,
        "funding_rate_sentiment": "bullish",
        "open_interest": 100_000_000,
        "long_short_ratio": 1.2,
        "top_trader_long_short_ratio": 1.05,
        "taker_buy_sell_ratio": 1.03,
        "mark_price": 3500.0,
        "index_price": 3498.0,
        "ticker_volume_24h": 500_000_000,
        "price_change_pct_24h": 2.0,
        "major_risks": ["some risk"],
        "funding_rate_8h_ago": 0.0003,
        "funding_rate_24h_ago": 0.0001,
        "oi_change_pct_24h": 8.0,
        "oi_change_pct_4h": 2.0,
        "premium_pct": 0.05,
        "liquidation_24h_long": 5_000_000,
        "liquidation_24h_short": 1_000_000,
    }
    ctx = normalize_futures_context(payload)
    assert ctx.symbol == "ETH"
    assert ctx.funding_rate == 0.0005
    assert ctx.oi_change_pct_24h == 8.0
    assert ctx.liquidation_24h_long == 5_000_000
    assert ctx.liquidation_24h_short == 1_000_000
    assert ctx.funding_rate_8h_ago == 0.0003
    assert len(ctx.major_risks) == 1
    print("PASS test_normalize_futures_context")


def test_normalize_futures_context_defaults():
    payload = {"symbol": "doge"}
    ctx = normalize_futures_context(payload)
    assert ctx.symbol == "DOGE"
    assert ctx.funding_rate == 0.0
    assert ctx.oi_change_pct_24h == 0.0
    assert ctx.liquidation_24h_long == 0.0
    print("PASS test_normalize_futures_context_defaults")
