from __future__ import annotations

import time
from typing import Any

_cache: dict[str, tuple[float, Any]] = {}

# Default TTLs in seconds
TTL_TOKEN = 30
TTL_SIGNAL = 30
TTL_AUDIT = 300
TTL_FUTURES = 15
TTL_MARKET_RANK = 60
TTL_WATCH_TODAY = 60
TTL_WALLET = 60
TTL_PORTFOLIO = 30
TTL_MEME = 60
TTL_ALPHA = 60


def _cache_key(command: str, entity: str = "") -> str:
    return f"{command}:{entity.upper()}" if entity else command


def cache_get(command: str, entity: str = "") -> Any | None:
    key = _cache_key(command, entity)
    entry = _cache.get(key)
    if entry is None:
        return None
    expiry, value = entry
    if time.monotonic() > expiry:
        _cache.pop(key, None)
        return None
    return value


def cache_set(command: str, entity: str, value: Any, ttl: float | None = None) -> None:
    if ttl is None:
        ttl = _DEFAULT_TTLS.get(command, TTL_TOKEN)
    key = _cache_key(command, entity)
    _cache[key] = (time.monotonic() + ttl, value)


def cache_clear() -> None:
    _cache.clear()


def cache_stats() -> dict[str, int]:
    now = time.monotonic()
    total = len(_cache)
    expired = sum(1 for expiry, _ in _cache.values() if now > expiry)
    return {"total": total, "active": total - expired, "expired": expired}


_DEFAULT_TTLS: dict[str, float] = {
    "token": TTL_TOKEN,
    "signal": TTL_SIGNAL,
    "audit": TTL_AUDIT,
    "futures": TTL_FUTURES,
    "market_rank": TTL_MARKET_RANK,
    "watch_today": TTL_WATCH_TODAY,
    "wallet": TTL_WALLET,
    "portfolio": TTL_PORTFOLIO,
    "meme": TTL_MEME,
    "alpha": TTL_ALPHA,
}
