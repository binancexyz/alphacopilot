import src.config as config
from src.services.factory import get_market_data_service
from src.services.mock_service import MockMarketDataService


def test_factory_defaults_to_mock():
    old_mode = config.settings.app_mode
    try:
        config.settings.app_mode = "mock"
        service = get_market_data_service()
    finally:
        config.settings.app_mode = old_mode
    assert isinstance(service, MockMarketDataService)
    assert service.get_alpha_context("BNB")["symbol"] == "BNB"
    assert service.get_futures_context("BTC")["symbol"] == "BTC"
    assert "_raw" in service.get_portfolio_context()
