from __future__ import annotations

from src.config import settings
from src.services.interfaces import MarketDataService
from src.services.live_service import LiveMarketDataService
from src.services.mock_service import MockMarketDataService


def get_market_data_service() -> MarketDataService:
    if settings.app_mode == "live":
        return LiveMarketDataService(
            base_url=settings.binance_skills_base_url,
            bridge_api_key=settings.bridge_api_key or settings.api_auth_key,
            bridge_api_header=settings.bridge_api_header,
        )
    return MockMarketDataService()
