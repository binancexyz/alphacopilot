from src.services.live_extractors import (
    extract_audit_context,
    extract_signal_context,
    extract_token_context,
    extract_wallet_context,
    extract_watch_today_context,
)
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


def test_extract_signal_context_enriches_market_and_futures_fields():
    raw = {
        "query-token-info": {
            "metadata": {"symbol": "DOGE", "name": "Dogecoin"},
            "dynamic": {
                "price": "0.151",
                "liquidity": "65000000",
                "holders": "120000",
                "volume24h": "5500000",
                "percentChange24h": "8.5",
                "marketCap": "18000000000",
                "smartMoneyHolders": "42",
                "smartMoneyHoldingPercent": "3.4",
            },
        },
        "crypto-market-rank": {
            "smart_money_inflow": [{"tokenName": "DOGE", "inflow": "250000", "traders": "12"}],
        },
        "trading-signal": {
            "data": [{
                "ticker": "DOGE",
                "direction": "buy",
                "status": "triggered",
                "alertPrice": "0.145",
                "smartMoneyCount": 4,
            }]
        },
        "derivatives-trading-usds-futures": {
            "funding_rate": {"data": [{"fundingRate": "0.0007"}]},
            "open_interest": {"openInterest": "123456"},
            "long_short_ratio": {"data": [{"longShortRatio": "1.6"}]},
            "mark_price": {"markPrice": "0.152"},
        },
        "query-token-audit": {"data": {"hasResult": True, "isSupported": True, "riskLevel": 1, "riskLevelEnum": "LOW", "riskItems": []}},
    }
    ctx = extract_signal_context(raw, "DOGE")
    assert ctx["current_price"] == 0.151
    assert ctx["liquidity"] == 65000000.0
    assert ctx["volume_24h"] == 5500000.0
    assert ctx["smart_money_inflow_usd"] == 250000.0
    assert ctx["funding_rate"] == 0.0007
    assert ctx["funding_sentiment"] == "bearish"


def test_extract_audit_context_preserves_validity_flags():
    raw = {
        "query-token-info": {"metadata": {"symbol": "BNB", "name": "BNB"}},
        "query-token-audit": {"data": {"hasResult": True, "isSupported": True, "riskLevel": 1, "riskLevelEnum": "LOW", "riskItems": []}},
    }
    ctx = extract_audit_context(raw, "BNB")
    assert ctx["has_result"] is True
    assert ctx["is_supported"] is True


def test_extract_audit_context_normalizes_snake_case_validity_flags():
    raw = {
        "query-token-info": {"metadata": {"symbol": "BNB", "name": "BNB"}},
        "query-token-audit": {"data": {"has_result": True, "is_supported": True, "risk_level": 2, "risk_level_enum": "MEDIUM", "risk_items": []}},
    }
    ctx = extract_audit_context(raw, "BNB")
    assert ctx["has_result"] is True
    assert ctx["is_supported"] is True
    assert ctx["risk_level"] == "Medium"


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


def test_extract_signal_context_marks_fresh_when_signal_has_data_but_age_is_missing():
    raw = {
        "trading-signal": {
            "data": [{
                "ticker": "DOGE",
                "direction": "buy",
                "status": "watch",
                "smartMoneyCount": 3,
            }]
        },
        "query-token-audit": {"data": {"hasResult": True, "isSupported": True, "riskLevel": 1, "riskLevelEnum": "LOW", "riskItems": []}},
    }
    ctx = extract_signal_context(raw, "DOGE")
    assert ctx["signal_freshness"] == "FRESH"


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
