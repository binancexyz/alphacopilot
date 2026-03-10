from src.services.factory import get_market_data_service
from src.services.mock_service import MockMarketDataService


def test_factory_defaults_to_mock():
    service = get_market_data_service()
    assert isinstance(service, MockMarketDataService)
