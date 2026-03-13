from __future__ import annotations

from src.services.live_extractors import extract_futures_context, extract_token_context


def test_extract_futures_context_basic():
    raw = {
        "derivatives-trading-usds-futures": {
            "mark_price": {"markPrice": "68050.0", "indexPrice": "68030.5"},
            "funding_rate": {"data": [{"fundingRate": "0.0001"}]},
            "open_interest": {"openInterest": "123456.0"},
            "long_short_ratio": {"data": [{"longShortRatio": "1.25"}]},
        },
        "query-token-info": {"metadata": {"symbol": "BTC", "name": "Bitcoin"}},
    }
    ctx = extract_futures_context(raw, "BTC")
    assert ctx["symbol"] == "BTC"
    assert ctx["funding_rate"] == 0.0001
    assert ctx["funding_rate_sentiment"] == "neutral"
    assert ctx["open_interest"] == 123456.0
    assert ctx["long_short_ratio"] == 1.25
    assert ctx["mark_price"] == 68050.0
    assert ctx["major_risks"] == []


def test_extract_futures_context_extreme_funding():
    raw = {
        "derivatives-trading-usds-futures": {
            "mark_price": {"markPrice": "2500.0"},
            "funding_rate": {"data": [{"fundingRate": "0.005"}]},
            "open_interest": {},
            "long_short_ratio": {"data": [{"longShortRatio": "3.0"}]},
        },
    }
    ctx = extract_futures_context(raw, "ETH")
    assert ctx["funding_rate_sentiment"] == "bearish"
    assert any("extreme" in r.lower() for r in ctx["major_risks"])
    assert any("crowded longs" in r.lower() for r in ctx["major_risks"])


def test_extract_futures_context_empty():
    ctx = extract_futures_context({}, "SOL")
    assert ctx["symbol"] == "SOL"
    assert ctx["funding_rate"] == 0.0
    assert ctx["funding_rate_sentiment"] == "neutral"
    assert ctx["open_interest"] == 0.0


def test_token_context_enriched_with_futures():
    raw = {
        "query-token-info": {
            "metadata": {"symbol": "BTC", "name": "Bitcoin"},
            "dynamic": {"price": "68000"},
        },
        "crypto-market-rank": {},
        "trading-signal": {},
        "query-token-audit": {},
        "derivatives-trading-usds-futures": {
            "mark_price": {"markPrice": "68050.0"},
            "funding_rate": {"data": [{"fundingRate": "0.0005"}]},
            "open_interest": {"openInterest": "500000"},
            "long_short_ratio": {"data": [{"longShortRatio": "1.5"}]},
        },
    }
    ctx = extract_token_context(raw, "BTC")
    assert "futures_funding_rate" in ctx
    assert ctx["futures_funding_rate"] == 0.0005
    assert ctx["futures_sentiment"] == "bearish"


def test_token_context_with_spot_enrichment():
    raw = {
        "query-token-info": {
            "metadata": {"symbol": "BNB"},
            "dynamic": {"price": "600"},
        },
        "crypto-market-rank": {},
        "trading-signal": {},
        "query-token-audit": {},
        "spot": {
            "lastPrice": "601.5",
            "volume": "100000",
            "priceChangePercent": "1.5",
        },
    }
    ctx = extract_token_context(raw, "BNB")
    assert ctx["cex_price"] == 601.5
    assert ctx["cex_volume_24h"] == 100000.0
    assert ctx["cex_price_change_pct_24h"] == 1.5
