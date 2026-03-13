from __future__ import annotations

import src.services.binance_skill_bridge as skill_bridge


class _FakeResponse:
    def __init__(self, payload, status_code: int = 200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"http {self.status_code}")

    def json(self):
        return self._payload


class _FakeClient:
    def __init__(self, responses):
        self._responses = responses

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return None

    def get(self, url, params=None, headers=None):
        payload = self._responses.get(("GET", url))
        if payload is None:
            raise RuntimeError(f"missing fake GET response for {url}")
        return _FakeResponse(payload)

    def post(self, url, json=None, headers=None):
        payload = self._responses.get(("POST", url))
        if payload is None:
            raise RuntimeError(f"missing fake POST response for {url}")
        return _FakeResponse(payload)


class _FakeHttpx:
    def __init__(self, responses):
        self._responses = responses

    def Client(self, timeout=0.0, follow_redirects=False):  # noqa: N802 - mirrors httpx API
        return _FakeClient(self._responses)


def test_fetch_live_bundle_builds_wallet_payload_with_skill_refs():
    responses = {
        ("GET", "https://web3.binance.com/bapi/defi/v3/public/wallet-direct/buw/wallet/address/pnl/active-position-list"): {
            "code": "000000",
            "success": True,
            "data": {"list": [{"symbol": "BNB", "price": "600", "remainQty": "2"}]},
        },
    }
    old = skill_bridge._require_httpx
    skill_bridge._require_httpx = lambda: _FakeHttpx(responses)
    try:
        bundle = skill_bridge.fetch_live_bundle("wallet", "0xabc")
    finally:
        skill_bridge._require_httpx = old

    assert "query-address-info" in bundle.raw
    assert bundle.meta["status"] == "live-ok"
    assert bundle.meta["failedSkills"] == []
    assert "query-address-info" in bundle.meta["skillRefs"]


def test_fetch_live_bundle_marks_partial_failure_without_dropping_other_skill_data():
    responses = {
        ("GET", "https://web3.binance.com/bapi/defi/v5/public/wallet-direct/buw/wallet/market/token/search"): {
            "code": "000000",
            "success": True,
            "data": [{"symbol": "DOGE", "name": "Dogecoin", "contractAddress": "0xdoge"}],
        },
        ("GET", "https://web3.binance.com/bapi/defi/v1/public/wallet-direct/buw/wallet/dex/market/token/meta/info"): {
            "code": "000000",
            "success": True,
            "data": {"symbol": "DOGE", "name": "Dogecoin", "contractAddress": "0xdoge"},
        },
        ("GET", "https://web3.binance.com/bapi/defi/v4/public/wallet-direct/buw/wallet/market/token/dynamic/info"): {
            "code": "000000",
            "success": True,
            "data": {"price": "0.12", "liquidity": "5000000"},
        },
        ("POST", "https://web3.binance.com/bapi/defi/v1/public/wallet-direct/buw/wallet/market/token/pulse/unified/rank/list"): {
            "code": "000000",
            "success": True,
            "data": {"tokens": [{"symbol": "DOGE", "holdersTop10Percent": "22"}]},
        },
        ("POST", "https://web3.binance.com/bapi/defi/v1/public/wallet-direct/buw/wallet/web/signal/smart-money"): {
            "code": "000000",
            "success": True,
            "data": [{"ticker": "DOGE", "contractAddress": "0xdoge", "direction": "buy", "status": "active"}],
        },
    }
    old = skill_bridge._require_httpx
    skill_bridge._require_httpx = lambda: _FakeHttpx(responses)
    try:
        bundle = skill_bridge.fetch_live_bundle("token", "DOGE")
    finally:
        skill_bridge._require_httpx = old

    assert bundle.meta["status"] == "partial-live"
    assert "query-token-audit" in bundle.meta["failedSkills"]
    assert "query-token-info" in bundle.raw
    assert "trading-signal" in bundle.raw
    assert "crypto-market-rank" in bundle.raw
