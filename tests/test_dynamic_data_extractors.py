from src.services.live_extractors import extract_token_context

def test_extract_token_context_dynamic_data():
    raw = {
        "query-token-info": {
            "search": [{"symbol": "TEST"}],
            "metadata": {"symbol": "TEST", "name": "Test Token"},
            "dynamic": {
                "price": "1.0",
                "volume24hBuy": "600",
                "volume24hSell": "400",
                "volume5m": "100",
                "volume1h": "1000",
                "volume4h": "4000",
                "volume24h": "24000",
                "percentChange5m": "0.1",
                "percentChange1h": "1.5",
                "percentChange4h": "-2.0",
                "percentChange24h": "10.0",
                "count24h": "1000",
                "count24hBuy": "600",
                "count24hSell": "400",
                "fdv": "1000000",
                "marketCap": "500000",
                "circulatingSupply": "500000",
                "totalSupply": "1000000",
                "priceHigh24h": "1.2",
                "priceLow24h": "0.9",
                "kolHolders": "10",
                "kolHoldingPercent": "5.0",
                "proHolders": "20",
                "proHoldingPercent": "10.0",
                "smartMoneyHolders": "5",
                "smartMoneyHoldingPercent": "2.5"
            }
        },
        "crypto-market-rank": {
            "smart_money_inflow": [
                {
                    "tokenName": "TEST",
                    "inflow": "5000",
                    "traders": "10"
                }
            ]
        }
    }
    
    context = extract_token_context(raw, "TEST")
    
    assert context["buy_sell_ratio"] == 0.6
    assert context["volume_5m"] == 100.0
    assert context["volume_1h"] == 1000.0
    assert context["volume_4h"] == 4000.0
    assert context["volume_24h"] == 24000.0
    assert context["pct_change_5m"] == 0.1
    assert context["pct_change_1h"] == 1.5
    assert context["pct_change_4h"] == -2.0
    assert context["pct_change_24h"] == 10.0
    assert context["tx_count_24h"] == 1000
    assert context["tx_buy_count_24h"] == 600
    assert context["tx_sell_count_24h"] == 400
    assert context["fdv"] == 1000000.0
    assert context["market_cap"] == 500000.0
    assert context["circulating_supply"] == 500000.0
    assert context["total_supply"] == 1000000.0
    assert context["price_high_24h"] == 1.2
    assert context["price_low_24h"] == 0.9
    assert context["kol_holders"] == 10
    assert context["kol_holding_pct"] == 5.0
    assert context["pro_holders"] == 20
    assert context["pro_holding_pct"] == 10.0
    assert context["smart_money_holders"] == 5
    assert context["smart_money_holding_pct"] == 2.5
    
    # Check smart money inflow
    assert context["smart_money_inflow_usd"] == 5000.0
    assert context["smart_money_inflow_traders"] == 10

def test_extract_token_context_incomplete_dynamic():
    raw = {
        "query-token-info": {
            "search": [{"symbol": "TEST"}],
            "metadata": {"symbol": "TEST"},
            "dynamic": {
                "price": "1.0",
                "volume24hBuy": "0",  # Test division by zero
                "volume24hSell": "0"
            }
        }
    }
    context = extract_token_context(raw, "TEST")
    assert "buy_sell_ratio" not in context
    assert context["volume_5m"] == 0.0
    assert context["tx_count_24h"] == 0
    assert "smart_money_inflow_usd" not in context
