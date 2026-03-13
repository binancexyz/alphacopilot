from src.services.live_extractors import extract_signal_context, extract_token_context, extract_wallet_context, extract_watch_today_context
from src.services.live_payload_examples import TOKEN_RAW_EXAMPLE


def test_extract_token_context():
    ctx = extract_token_context(TOKEN_RAW_EXAMPLE, "BNB")
    assert ctx["symbol"] == "BNB"
    assert ctx["signal_status"] == "watch"
    assert "Signal may weaken if volume does not confirm." in ctx["major_risks"]


def test_extract_signal_context():
    raw = {
        "trading-signal": {
            "data": [{
                "ticker": "DOGE",
                "direction": "buy",
                "status": "active",
                "alertPrice": "0.12",
                "currentPrice": "0.15",
                "maxGain": "5.2",
                "exitRate": 22,
                "smartMoneyCount": 4,
                "launchPlatform": "Pumpfun",
            }]
        },
        "query-token-audit": {"data": {"hasResult": True, "isSupported": True, "riskLevel": 1, "riskLevelEnum": "LOW", "riskItems": []}},
    }
    ctx = extract_signal_context(raw, "DOGE")
    assert ctx["token"] == "DOGE"
    assert ctx["signal_status"] == "active"
    assert ctx["current_price"] == 0.15


def test_extract_wallet_context_from_address_list():
    raw = {
        "query-address-info": {
            "list": [
                {"symbol": "BNB", "price": "600", "remainQty": "2", "percentChange24h": "5"},
                {"symbol": "DOGE", "price": "0.2", "remainQty": "1000", "percentChange24h": "1"},
            ]
        }
    }
    ctx = extract_wallet_context(raw, "0x123")
    assert ctx["holdings_count"] == 2
    assert ctx["portfolio_value"] > 0
    assert ctx["top_holdings"][0]["symbol"] == "BNB"


def test_extract_watch_today_context_from_skill_shapes():
    raw = {
        "crypto-market-rank": {
            "data": {
                "leaderBoardList": [
                    {"socialHypeInfo": {"socialSummaryBriefTranslated": "AI tokens are leading social hype."}}
                ]
            }
        },
        "meme-rush": {
            "data": [
                {"name": {"topicNameEn": "AI Meme Rotation"}, "topicNetInflow": "12000"}
            ]
        },
        "trading-signal": {
            "data": [
                {"ticker": "DOGE", "direction": "buy", "status": "active"}
            ]
        },
    }
    ctx = extract_watch_today_context(raw)
    assert ctx["top_narratives"]
    assert "DOGE: BUY (active)" in ctx["strongest_signals"]
