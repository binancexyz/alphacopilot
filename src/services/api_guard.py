from __future__ import annotations

from collections import defaultdict, deque
from time import time
from typing import Deque

from fastapi import Header, HTTPException, Request

from src.config import settings

_RATE_BUCKETS: dict[str, Deque[float]] = defaultdict(deque)


def enforce_api_guard(request: Request, api_key: str | None = Header(default=None, alias="X-API-Key")) -> None:
    _enforce_auth(api_key, request)
    _enforce_rate_limit(request)


def _enforce_auth(api_key: str | None, request: Request) -> None:
    if not settings.api_auth_enabled:
        return
    expected = settings.api_auth_key.strip()
    if not expected:
        raise HTTPException(status_code=500, detail="API auth is enabled but API_AUTH_KEY is not configured.")

    provided = request.headers.get(settings.api_auth_header) or api_key or ""
    if provided != expected:
        raise HTTPException(status_code=401, detail="Unauthorized.")


def _enforce_rate_limit(request: Request) -> None:
    if not settings.api_rate_limit_enabled:
        return
    now = time()
    window = max(settings.api_rate_limit_window_seconds, 1)
    limit = max(settings.api_rate_limit_requests, 1)
    client_host = getattr(request.client, "host", None) or "unknown"
    bucket = _RATE_BUCKETS[client_host]
    while bucket and now - bucket[0] > window:
        bucket.popleft()
    if len(bucket) >= limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded.")
    bucket.append(now)


def guard_status() -> dict[str, object]:
    return {
        "auth_enabled": settings.api_auth_enabled,
        "auth_header": settings.api_auth_header,
        "rate_limit_enabled": settings.api_rate_limit_enabled,
        "rate_limit_requests": settings.api_rate_limit_requests,
        "rate_limit_window_seconds": settings.api_rate_limit_window_seconds,
    }
