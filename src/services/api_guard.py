from __future__ import annotations

import hmac
from collections import defaultdict, deque
from time import time
from typing import Deque

from fastapi import HTTPException, Request

from src.config import settings

_RATE_BUCKETS: dict[str, Deque[float]] = defaultdict(deque)
_MAX_TRACKED_CLIENTS = 10_000


def enforce_api_guard(request: Request) -> None:
    _enforce_request_auth(
        request,
        enabled=settings.api_auth_enabled,
        expected_key=settings.api_auth_key,
        header_name=settings.api_auth_header,
        service_name="API",
    )
    _enforce_rate_limit(request)


def enforce_bridge_guard(request: Request) -> None:
    expected = (settings.bridge_api_key or settings.api_auth_key).strip()
    if expected:
        _enforce_request_auth(
            request,
            enabled=True,
            expected_key=expected,
            header_name=settings.bridge_api_header,
            service_name="bridge",
        )
    _enforce_rate_limit(request)


def _enforce_request_auth(
    request: Request,
    *,
    enabled: bool,
    expected_key: str,
    header_name: str,
    service_name: str,
) -> None:
    if not enabled:
        return
    expected = expected_key.strip()
    if not expected:
        raise HTTPException(status_code=500, detail=f"{service_name} auth is enabled but no auth key is configured.")

    provided = request.headers.get(header_name, "")
    if not hmac.compare_digest(provided, expected):
        raise HTTPException(status_code=401, detail="Unauthorized.")


def _enforce_rate_limit(request: Request) -> None:
    if not settings.api_rate_limit_enabled:
        return
    now = time()
    window = max(settings.api_rate_limit_window_seconds, 1)
    limit = max(settings.api_rate_limit_requests, 1)
    client_host = getattr(request.client, "host", None) or "unknown"

    if client_host not in _RATE_BUCKETS and len(_RATE_BUCKETS) >= _MAX_TRACKED_CLIENTS:
        _evict_stale_buckets(now, window)

    bucket = _RATE_BUCKETS[client_host]
    while bucket and now - bucket[0] > window:
        bucket.popleft()
    if len(bucket) >= limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded.")
    bucket.append(now)


def _evict_stale_buckets(now: float, window: float) -> None:
    stale = [key for key, bucket in _RATE_BUCKETS.items() if not bucket or now - bucket[-1] > window]
    for key in stale:
        del _RATE_BUCKETS[key]


def guard_status() -> dict[str, object]:
    return {
        "auth_enabled": settings.api_auth_enabled,
        "auth_header": settings.api_auth_header,
        "rate_limit_enabled": settings.api_rate_limit_enabled,
        "rate_limit_requests": settings.api_rate_limit_requests,
        "rate_limit_window_seconds": settings.api_rate_limit_window_seconds,
    }


def bridge_guard_status() -> dict[str, object]:
    bridge_auth_key = (settings.bridge_api_key or settings.api_auth_key).strip()
    return {
        "auth_enabled": bool(bridge_auth_key),
        "auth_header": settings.bridge_api_header,
        "rate_limit_enabled": settings.api_rate_limit_enabled,
        "rate_limit_requests": settings.api_rate_limit_requests,
        "rate_limit_window_seconds": settings.api_rate_limit_window_seconds,
    }
