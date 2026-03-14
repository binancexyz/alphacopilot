import src.analyzers.portfolio_analysis as portfolio_analysis


import src.analyzers.portfolio_analysis as portfolio_analysis

class DummyLiveService:
    def __init__(self, responses):
        self.responses = responses
        
    def get_portfolio_context(self):
        return {
            "_raw": {
                "assets": {"data": self.responses["account"]["balances"]},
                "margin-trading": self.responses.get("margin", {}),
            },
            "prices": self.responses["prices_dict"]
        }


def test_analyze_portfolio_builds_balanced_snapshot():
    responses = {
        "account": {
            "balances": [
                {"asset": "USDT", "free": "1000", "locked": "0"},
                {"asset": "BNB", "free": "1", "locked": "0"},
                {"asset": "BTC", "free": "0.01", "locked": "0"},
            ]
        },
        "prices_dict": {
            "BNB": "600",
            "BTC": "80000",
            "USDT": "1",
        },
    }
    old_service = portfolio_analysis.LiveMarketDataService
    try:
        portfolio_analysis.LiveMarketDataService = lambda **kwargs: DummyLiveService(responses)
        brief = portfolio_analysis.analyze_portfolio()
    finally:
        portfolio_analysis.LiveMarketDataService = old_service

    assert brief.entity == "Portfolio: Binance Spot"
    assert "Estimated visible Spot value" in brief.why_it_matters
    assert "Stablecoins are" in brief.why_it_matters
    assert "Lead exposure groups" in brief.why_it_matters
    assert any(tag.name == "Top Concentration" for tag in brief.risk_tags)
    assert any(tag.name == "Stablecoin Share" for tag in brief.risk_tags)
    assert any(tag.name == "Lead Group" for tag in brief.risk_tags)
    assert "USDT" in (brief.beginner_note or "")


def test_analyze_portfolio_normalizes_ld_assets():
    responses = {
        "account": {
            "balances": [
                {"asset": "LDUSDT", "free": "10", "locked": "0"},
                {"asset": "LDETH", "free": "1", "locked": "0"},
            ]
        },
        "prices_dict": {
            "ETH": "2000",
            "BTC": "80000",
            "USDT": "1",
        },
    }
    old_service = portfolio_analysis.LiveMarketDataService
    try:
        portfolio_analysis.LiveMarketDataService = lambda **kwargs: DummyLiveService(responses)
        brief = portfolio_analysis.analyze_portfolio()
    finally:
        portfolio_analysis.LiveMarketDataService = old_service

    note = brief.beginner_note or ""
    assert "USDT" in note
    assert "ETH" in note
    assert "LDUSDT" not in note
    assert "estimated Spot snapshot" in " ".join((tag.note or "") for tag in brief.risk_tags)


def test_analyze_portfolio_includes_margin_exposure():
    responses = {
        "account": {
            "balances": [
                {"asset": "USDT", "free": "1000", "locked": "0"},
                {"asset": "BTC", "free": "0.01", "locked": "0"},
            ]
        },
        "margin": {
            "marginLevel": "2.1",
            "totalLiabilityOfBtc": "0.0100",
            "totalNetAssetOfBtc": "0.0200",
            "userAssets": [
                {"asset": "BTC", "borrowed": "0.0100", "interest": "0.0001", "netAsset": "0.0200"},
            ],
        },
        "prices_dict": {
            "BTC": "80000",
            "USDT": "1",
        },
    }
    old_service = portfolio_analysis.LiveMarketDataService
    try:
        portfolio_analysis.LiveMarketDataService = lambda **kwargs: DummyLiveService(responses)
        brief = portfolio_analysis.analyze_portfolio()
    finally:
        portfolio_analysis.LiveMarketDataService = old_service

    assert brief.quick_verdict == "Levered posture. Margin exposure is material."
    assert any(tag.name == "Margin Exposure" for tag in brief.risk_tags)
    assert any("Margin borrowed is about" in risk for risk in brief.top_risks)
