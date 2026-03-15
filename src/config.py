from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load_local_env() -> None:
    for candidate in (ROOT / '.env.local', ROOT / '.env'):
        if not candidate.exists():
            continue
        for raw_line in candidate.read_text(encoding='utf-8').splitlines():
            line = raw_line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


_load_local_env()


@dataclass
class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    app_mode: str = os.getenv("APP_MODE", "mock")
    binance_skills_base_url: str = os.getenv("BINANCE_SKILLS_BASE_URL", "")
    binance_api_key: str = os.getenv("BINANCE_API_KEY", "")
    binance_api_secret: str = os.getenv("BINANCE_API_SECRET", "")
    bridge_api_key: str = os.getenv("BRIDGE_API_KEY", "")
    bridge_api_header: str = os.getenv("BRIDGE_API_HEADER", "X-API-Key")
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
    if settings.app_env != "development" and not settings.api_auth_enabled:
        warnings.append("API_AUTH_ENABLED is false outside development — set API_AUTH_ENABLED=true and provide API_AUTH_KEY for production.")
    if settings.api_port < 1 or settings.api_port > 65535:
        warnings.append(f"API_PORT={settings.api_port} is outside valid range (1-65535).")
    if settings.bridge_http_timeout_seconds <= 0:
        warnings.append("BRIDGE_HTTP_TIMEOUT_SECONDS must be positive.")
    if settings.api_rate_limit_enabled and settings.api_rate_limit_window_seconds <= 0:
        warnings.append("API_RATE_LIMIT_WINDOW_SECONDS must be positive.")
    return warnings


def config_errors(service: str = "all") -> list[str]:
    errors: list[str] = []
    env = settings.app_env.strip().lower()
    locked_down_env = env not in {"", "development", "dev", "local", "test"}

    service_key = service.strip().lower() or "all"
    if locked_down_env and settings.app_mode == "live" and not settings.binance_skills_base_url:
        errors.append("APP_MODE=live requires BINANCE_SKILLS_BASE_URL outside development.")
    if locked_down_env and service_key in {"all", "api"} and (not settings.api_auth_enabled or not settings.api_auth_key.strip()):
        errors.append("APP_ENV outside development requires API_AUTH_ENABLED=true and a non-empty API_AUTH_KEY.")
    if locked_down_env and service_key in {"all", "bridge"}:
        bridge_auth_key = (settings.bridge_api_key or settings.api_auth_key).strip()
        if not bridge_auth_key:
            errors.append("APP_ENV outside development requires BRIDGE_API_KEY or API_AUTH_KEY for bridge access.")
    return errors
