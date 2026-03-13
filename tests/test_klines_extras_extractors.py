from src.services.live_extractors import extract_token_context, extract_futures_context

def test_extract_spot_alpha_klines_and_trades():
    raw = {
        "spot": {
            "ticker": {"lastPrice": "1.0"},
            "kline": {
                "data": [
                    [1, 2, 3, 4, "1.5", "100"],
                    [1, 2, 3, 4, "1.6", "120"] # latest
                ]
            },
            "recent_trades": {
                "data": [
                    {"price": "1.5"}, {"price": "1.6"}
                ]
            }
        },
        "alpha": {
            "is_alpha_listed": True,
            "ticker": {"price": "1.8"},
            "kline": [
                [1, 2, 3, 4, "1.7", "100"],
                [1, 2, 3, 4, "1.9", "100"] # latest
            ]
        }
    }
    
    context = extract_token_context(raw, "TOKEN")
    
    # Check Spot
    assert context["spot_kline_candles"] == 2
    assert context["spot_kline_latest_close"] == 1.6
    assert context["spot_recent_trades_count"] == 2
    
    # Check Alpha
    assert context["alpha_kline_candles"] == 2
    assert context["alpha_kline_latest_close"] == 1.9

def test_extract_futures_klines_and_ticker():
    raw = {
        "derivatives-trading-usds-futures": {
            "funding_rate": {"data": [{"fundingRate": "0"}]},
            "open_interest": {"openInterest": "0"},
            "long_short_ratio": {"data": [{"longShortRatio": "1"}]},
            "mark_price": {"markPrice": "10.0"},
            "ticker": {
                "volume": "1000",
                "priceChangePercent": "5.0"
            },
            "kline": [
                [1, 2, 3, 4, "9.5", "100"],
                [1, 2, 3, 4, "10.5", "150"] # latest
            ]
        }
    }
    
    context = extract_futures_context(raw, "TOKEN")
    
    # New Extra Fields
    assert context["futures_ticker_volume_24h"] == 1000.0
    assert context["futures_price_change_pct_24h"] == 5.0
    assert context["futures_kline_candles"] == 2
    assert context["futures_kline_latest_close"] == 10.5
