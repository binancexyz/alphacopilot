from src.analyzers.futures_analysis import analyze_futures


def test_futures_oi_trend_interpretation():
    ctx = {
        "symbol": "BTC",
        "funding_rate": 0.0005,
        "funding_rate_sentiment": "bullish",
        "open_interest": 500_000_000,
        "long_short_ratio": 1.3,
        "top_trader_long_short_ratio": 1.05,
        "taker_buy_sell_ratio": 1.05,
        "mark_price": 65000.0,
        "index_price": 64980.0,
        "ticker_volume_24h": 2_000_000_000,
        "price_change_pct_24h": 2.5,
        "major_risks": [],
        "oi_change_pct_24h": 8.0,
        "oi_change_pct_4h": 2.5,
        "funding_rate_8h_ago": 0.0003,
        "funding_rate_24h_ago": 0.0001,
        "premium_pct": 0.03,
        "liquidation_24h_long": 0.0,
        "liquidation_24h_short": 0.0,
    }
    brief = analyze_futures("BTC", ctx)
    assert brief.entity == "Futures · BTC"
    tag_names = [t.name for t in brief.risk_tags]
    assert "Funding Trend" in tag_names
    assert "Open Interest" in tag_names
    assert "Basis/Premium" in tag_names
    # OI rising + price rising should show conviction longs
    oi_tag = next(t for t in brief.risk_tags if t.name == "Open Interest")
    assert "conviction longs" in oi_tag.note.lower() or "rising" in oi_tag.note.lower()
    print("PASS test_futures_oi_trend_interpretation")


def test_futures_liquidation_data():
    ctx = {
        "symbol": "ETH",
        "funding_rate": -0.002,
        "funding_rate_sentiment": "bearish",
        "open_interest": 100_000_000,
        "long_short_ratio": 0.8,
        "top_trader_long_short_ratio": 0.95,
        "taker_buy_sell_ratio": 0.92,
        "mark_price": 3500.0,
        "index_price": 3498.0,
        "ticker_volume_24h": 500_000_000,
        "price_change_pct_24h": -3.5,
        "major_risks": [],
        "liquidation_24h_long": 15_000_000,
        "liquidation_24h_short": 2_000_000,
        "oi_change_pct_24h": -6.0,
        "oi_change_pct_4h": -2.0,
        "funding_rate_8h_ago": -0.001,
        "funding_rate_24h_ago": 0.0002,
        "premium_pct": -0.06,
    }
    brief = analyze_futures("ETH", ctx)
    tag_names = [t.name for t in brief.risk_tags]
    assert "Liquidations 24h" in tag_names
    liq_tag = next(t for t in brief.risk_tags if t.name == "Liquidations 24h")
    assert "long" in liq_tag.note.lower()
    assert liq_tag.level == "High"
    # Squeeze risk should be elevated
    squeeze_tag = next(t for t in brief.risk_tags if t.name == "Squeeze Risk")
    assert squeeze_tag.level in ("High", "Medium")
    print("PASS test_futures_liquidation_data")


def test_futures_funding_trend_rising():
    ctx = {
        "symbol": "SOL",
        "funding_rate": 0.0015,
        "funding_rate_sentiment": "bullish",
        "open_interest": 50_000_000,
        "long_short_ratio": 1.1,
        "top_trader_long_short_ratio": 1.0,
        "taker_buy_sell_ratio": 1.0,
        "mark_price": 150.0,
        "index_price": 149.9,
        "ticker_volume_24h": 100_000_000,
        "price_change_pct_24h": 1.0,
        "major_risks": [],
        "funding_rate_8h_ago": 0.001,
        "funding_rate_24h_ago": 0.0005,
        "oi_change_pct_24h": 0.0,
        "oi_change_pct_4h": 0.0,
        "premium_pct": 0.0,
        "liquidation_24h_long": 0.0,
        "liquidation_24h_short": 0.0,
    }
    brief = analyze_futures("SOL", ctx)
    funding_tag = next(t for t in brief.risk_tags if t.name == "Funding Trend")
    assert "rising" in funding_tag.note.lower()
    assert funding_tag.level == "High"
    print("PASS test_futures_funding_trend_rising")


def test_futures_empty_context_still_works():
    ctx = {
        "symbol": "DOGE",
        "funding_rate": 0.0,
        "funding_rate_sentiment": "neutral",
        "open_interest": 0.0,
        "long_short_ratio": 1.0,
        "top_trader_long_short_ratio": 1.0,
        "taker_buy_sell_ratio": 1.0,
        "mark_price": 0.0,
        "index_price": 0.0,
        "ticker_volume_24h": 0.0,
        "price_change_pct_24h": 0.0,
        "major_risks": ["No live data"],
    }
    brief = analyze_futures("DOGE", ctx)
    assert brief.entity == "Futures · DOGE"
    assert brief.signal_quality == "Low"
    print("PASS test_futures_empty_context_still_works")
