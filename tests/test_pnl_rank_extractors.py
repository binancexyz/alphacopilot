from src.services.live_extractors import extract_watch_today_context

def test_extract_watch_today_context_pnl_rank():
    raw = {
        "crypto-market-rank": {
            "top_traders": [
                {
                    "address": "0x1234567890abcdef1234567890abcdef12345678",
                    "realizedPnl": "50000",
                    "winRate": "85",
                    "topEarningTokens": [
                        {"tokenSymbol": "BTC"},
                        {"tokenSymbol": "ETH"},
                        {"tokenSymbol": "SOL"}
                    ]
                },
                {
                    "addressLabel": "SmartTrader_99",
                    "realizedPnl": "10000",
                    "winRate": "60",
                    "topEarningTokens": [
                        {"tokenSymbol": "DOGE"}
                    ]
                },
                {
                    "address": "0xabc",
                    # Missing realizedPnl and winRate to test fallbacks
                }
            ]
        }
    }
    
    context = extract_watch_today_context(raw)
    
    top_traders = context.get("top_traders", [])
    assert len(top_traders) == 3
    
    # Check first trader format
    assert "0x1234…5678" in top_traders[0]
    assert "PnL $50K" in top_traders[0]
    assert "WR 85%" in top_traders[0]
    assert "top: BTC, ETH, SOL" in top_traders[0]
    
    # Check second trader format
    assert "SmartTrader_99" in top_traders[1]
    assert "PnL $10K" in top_traders[1]
    assert "WR 60%" in top_traders[1]
    assert "top: DOGE" in top_traders[1]
    
    # Check third trader format (fallbacks)
    assert "0xabc" in top_traders[2]
    assert "PnL" not in top_traders[2]
    assert "WR" not in top_traders[2]
    assert "top:" not in top_traders[2]
