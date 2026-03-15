from src.services.factory import get_market_data_service
from src.services.mock_service import MockMarketDataService


def test_factory_defaults_to_mock():
    service = get_market_data_service()
    assert isinstance(service, MockMarketDataService)
    assert service.get_alpha_context("BNB")["symbol"] == "BNB"
    assert service.get_futures_context("BTC")["symbol"] == "BTC"
    assert "_raw" in service.get_portfolio_context()
