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
    coinmarketcap_api_key: str = os.getenv("COINMARKETCAP_API_KEY", "")
    bridge_live_enabled: bool = os.getenv("BRIDGE_LIVE_ENABLED", "false").lower() == "true"
    bridge_default_chain_id: str = os.getenv("BRIDGE_DEFAULT_CHAIN_ID", "56")
    bridge_http_timeout_seconds: float = float(os.getenv("BRIDGE_HTTP_TIMEOUT_SECONDS", "20"))
    bridge_http_retries: int = int(os.getenv("BRIDGE_HTTP_RETRIES", "2"))
    bridge_healthcheck_enabled: bool = os.getenv("BRIDGE_HEALTHCHECK_ENABLED", "true").lower() == "true"
    api_auth_enabled: bool = os.getenv("API_AUTH_ENABLED", "false").lower() == "true"
    api_auth_key: str = os.getenv("API_AUTH_KEY", "")
    api_auth_header: str = os.getenv("API_AUTH_HEADER", "X-API-Key")
    api_rate_limit_enabled: bool = os.getenv("API_RATE_LIMIT_ENABLED", "true").lower() == "true"
    api_rate_limit_requests: int = int(os.getenv("API_RATE_LIMIT_REQUESTS", "60"))
    api_rate_limit_window_seconds: int = int(os.getenv("API_RATE_LIMIT_WINDOW_SECONDS", "60"))
    api_request_logging_enabled: bool = os.getenv("API_REQUEST_LOGGING_ENABLED", "true").lower() == "true"


settings = Settings()


def config_warnings() -> list[str]:
    warnings: list[str] = []
    if settings.app_mode == "live" and not settings.binance_skills_base_url:
        warnings.append("APP_MODE=live but BINANCE_SKILLS_BASE_URL is not configured.")
    if settings.api_auth_enabled and not settings.api_auth_key:
        warnings.append("API_AUTH_ENABLED=true but API_AUTH_KEY is empty.")
    if settings.api_rate_limit_enabled and settings.api_rate_limit_requests <= 0:
        warnings.append("API rate limiting is enabled but API_RATE_LIMIT_REQUESTS is not positive.")
    return warnings
