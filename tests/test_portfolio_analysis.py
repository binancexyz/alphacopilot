import src.analyzers.portfolio_analysis as portfolio_analysis


class DummyClient:
    def __init__(self, responses):
        self.responses = responses

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def get(self, url, headers=None):
        class Resp:
            def __init__(self, payload):
                self.payload = payload

            def raise_for_status(self):
                return None

            def json(self):
                return self.payload
        if "/api/v3/account" in url:
            return Resp(self.responses["account"])
        if "/api/v3/ticker/price" in url:
            return Resp(self.responses["prices"])
        raise AssertionError(url)


def test_analyze_portfolio_builds_balanced_snapshot():
    old_client = portfolio_analysis._httpx_client
    old_key = portfolio_analysis.settings.binance_api_key
    old_secret = portfolio_analysis.settings.binance_api_secret
    portfolio_analysis.settings.binance_api_key = "k"
    portfolio_analysis.settings.binance_api_secret = "s"
    portfolio_analysis._httpx_client = lambda *a, **k: DummyClient({
        "account": {
            "balances": [
                {"asset": "USDT", "free": "1000", "locked": "0"},
                {"asset": "BNB", "free": "1", "locked": "0"},
                {"asset": "BTC", "free": "0.01", "locked": "0"},
            ]
        },
        "prices": [
            {"symbol": "BNBUSDT", "price": "600"},
            {"symbol": "BTCUSDT", "price": "80000"},
        ],
    })
    try:
        brief = portfolio_analysis.analyze_portfolio()
    finally:
        portfolio_analysis._httpx_client = old_client
        portfolio_analysis.settings.binance_api_key = old_key
        portfolio_analysis.settings.binance_api_secret = old_secret

    assert brief.entity == "Portfolio: Binance Spot"
    assert "Estimated visible Spot value" in brief.why_it_matters
    assert any(tag.name == "Top Concentration" for tag in brief.risk_tags)
    assert "USDT" in (brief.beginner_note or "")
