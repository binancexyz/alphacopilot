from src.services.live_extractors import extract_token_context

def test_extract_token_context_spot_and_kline():
    raw = {
        "spot": {
            "ticker": {
                "lastPrice": "50000.0",
                "volume": "100.5",
                "priceChangePercent": "5.5"
            },
            "depth": {
                "bids": [
                    ["49900.0", "1.5"],
                    ["49850.0", "2.0"]
                ],
                "asks": [
                    ["50100.0", "0.5"],
                    ["50200.0", "3.0"],
                    ["50300.0", "1.0"]
                ]
            }
        },
        "query-token-info": {
            "kline": [
                [0.1, 0.2, 0.05, 0.15, 2000, 123456789, 10],
                [0.15, 0.18, 0.12, 0.16, 2500, 123456800, 12]  # Latest candle
            ]
        }
    }
    
    context = extract_token_context(raw, "BTC")
    
    # Check spot ticker
    assert context["cex_price"] == 50000.0
    assert context["cex_volume_24h"] == 100.5
    assert context["cex_price_change_pct_24h"] == 5.5
    
    # Check spot depth
    assert context["spot_bid_depth"] == 2
    assert context["spot_ask_depth"] == 3
    assert context["spot_top_bid"] == 49900.0
    assert context["spot_top_ask"] == 50100.0
    
    # Check kline
    assert context["kline_candles"] == 2
    assert context["kline_latest_close"] == 0.16
    assert context["kline_latest_volume"] == 2500.0

def test_extract_token_context_legacy_spot():
    raw = {
        "spot": {
            "lastPrice": "50000.0",
            "volume": "100.5",
            "priceChangePercent": "5.5"
        }
    }
    
    context = extract_token_context(raw, "BTC")
    
    assert context["cex_price"] == 50000.0
    assert "spot_bid_depth" not in context
    assert "kline_candles" not in context
