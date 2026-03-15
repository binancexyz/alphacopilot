from fastapi import HTTPException
from starlette.requests import Request

import src.services.api_guard as api_guard


def _request(headers=None, client_host='127.0.0.1'):
    scope = {
        'type': 'http',
        'method': 'GET',
        'path': '/health',
        'headers': [(k.lower().encode(), v.encode()) for k, v in (headers or {}).items()],
        'client': (client_host, 12345),
    }
    return Request(scope)


def test_guard_status_shape():
    status = api_guard.guard_status()
    assert 'auth_enabled' in status
    assert 'rate_limit_enabled' in status


def test_bridge_guard_status_shape():
    status = api_guard.bridge_guard_status()
    assert 'auth_enabled' in status
    assert 'auth_header' in status


def test_rate_limit_allows_first_request():
    old_enabled = api_guard.settings.api_rate_limit_enabled
    old_requests = api_guard.settings.api_rate_limit_requests
    old_window = api_guard.settings.api_rate_limit_window_seconds
    api_guard._RATE_BUCKETS.clear()
    api_guard.settings.api_rate_limit_enabled = True
    api_guard.settings.api_rate_limit_requests = 2
    api_guard.settings.api_rate_limit_window_seconds = 60
    try:
        api_guard._enforce_rate_limit(_request())
    finally:
        api_guard.settings.api_rate_limit_enabled = old_enabled
        api_guard.settings.api_rate_limit_requests = old_requests
        api_guard.settings.api_rate_limit_window_seconds = old_window


def test_auth_rejects_wrong_key():
    old_enabled = api_guard.settings.api_auth_enabled
    old_key = api_guard.settings.api_auth_key
    old_header = api_guard.settings.api_auth_header
    api_guard.settings.api_auth_enabled = True
    api_guard.settings.api_auth_key = 'secret'
    api_guard.settings.api_auth_header = 'X-API-Key'
    try:
        try:
            api_guard.enforce_api_guard(_request(headers={'X-API-Key': 'wrong'}))
            raise AssertionError('expected unauthorized')
        except HTTPException as exc:
            assert exc.status_code == 401
    finally:
        api_guard.settings.api_auth_enabled = old_enabled
        api_guard.settings.api_auth_key = old_key
        api_guard.settings.api_auth_header = old_header


def test_bridge_auth_rejects_wrong_key():
    old_key = api_guard.settings.bridge_api_key
    old_header = api_guard.settings.bridge_api_header
    api_guard.settings.bridge_api_key = 'bridge-secret'
    api_guard.settings.bridge_api_header = 'X-Bridge-Key'
    try:
        try:
            api_guard.enforce_bridge_guard(_request(headers={'X-Bridge-Key': 'wrong'}))
            raise AssertionError('expected unauthorized')
        except HTTPException as exc:
            assert exc.status_code == 401
    finally:
        api_guard.settings.bridge_api_key = old_key
        api_guard.settings.bridge_api_header = old_header
