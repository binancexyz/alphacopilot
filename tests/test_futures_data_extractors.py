from src.services.live_extractors import extract_futures_context, _enrich_futures_sentiment

def test_extract_futures_context():
    raw = {
        "derivatives-trading-usds-futures": {
            "funding_rate": {"data": [{"fundingRate": "-0.00015"}]},
            "open_interest": {"openInterest": "5000000.0"},
            "long_short_ratio": {"data": [{"longShortRatio": "1.2"}]},
            "mark_price": {"markPrice": "62000.0", "indexPrice": "62010.0"},
            "taker_volume": {"data": [{"buySellRatio": "1.05", "buyVol": "100.0", "sellVol": "95.0"}]},
            "top_trader_ls": {"data": [{"longShortRatio": "1.5"}]}
        }
    }
    
    context = extract_futures_context(raw, "BTC")
    
    # Existing fields
    assert context["funding_rate"] == -0.00015
    assert context["funding_rate_sentiment"] == "bullish"
    assert context["open_interest"] == 5000000.0
    assert context["long_short_ratio"] == 1.2
    
    # New fields
    assert context["taker_buy_sell_ratio"] == 1.05
    assert context["taker_buy_volume_1d"] == 100.0
    assert context["taker_sell_volume_1d"] == 95.0
    assert context["top_trader_long_short_ratio"] == 1.5

def test_enrich_futures_sentiment():
    context = {}
    futures_payload = {
        "funding_rate": {"data": [{"fundingRate": "0.0004"}]},
        "open_interest": {"openInterest": "2000000.0"},
        "long_short_ratio": {"data": [{"longShortRatio": "2.6"}]},
        "mark_price": {"markPrice": "4000.0"},
        "taker_volume": {"data": [{"buySellRatio": "0.95", "buyVol": "95.0", "sellVol": "100.0"}]},
        "top_trader_ls": {"data": [{"longShortRatio": "2.8"}]}
    }
    
    _enrich_futures_sentiment(context, futures_payload)
    
    # Existing fields
    assert context["futures_funding_rate"] == 0.0004
    assert context["futures_open_interest"] == 2000000.0
    assert context["futures_long_short_ratio"] == 2.6
    
    # New fields
    assert context["futures_taker_buy_sell_ratio"] == 0.95
    assert context["futures_taker_buy_volume_1d"] == 95.0
    assert context["futures_taker_sell_volume_1d"] == 100.0
    assert context["futures_top_trader_long_short_ratio"] == 2.8
