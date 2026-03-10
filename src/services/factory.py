from __future__ import annotations

from src.config import settings
from src.services.interfaces import MarketDataService
from src.services.live_service import LiveMarketDataService
from src.services.mock_service import MockMarketDataService


def get_market_data_service() -> MarketDataService:
    if settings.app_mode == "live":
        return LiveMarketDataService(
            base_url=settings.binance_skills_base_url,
            api_key=settings.binance_api_key,
            api_secret=settings.binance_api_secret,
        )
    return MockMarketDataService()
