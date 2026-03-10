from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    app_mode: str = os.getenv("APP_MODE", "mock")
    binance_skills_base_url: str = os.getenv("BINANCE_SKILLS_BASE_URL", "")
    binance_api_key: str = os.getenv("BINANCE_API_KEY", "")
    binance_api_secret: str = os.getenv("BINANCE_API_SECRET", "")
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    square_api_key: str = os.getenv("BINANCE_SQUARE_API_KEY", "")
    square_api_base_url: str = os.getenv("BINANCE_SQUARE_API_BASE_URL", "https://www.binance.com")
    square_api_publish_path: str = os.getenv("BINANCE_SQUARE_API_PUBLISH_PATH", "/bapi/composite/v1/public/pgc/openApi/content/add")
    square_api_key_header: str = os.getenv("BINANCE_SQUARE_API_KEY_HEADER", "X-Square-OpenAPI-Key")


settings = Settings()
