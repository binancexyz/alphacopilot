from __future__ import annotations

"""
Template helpers for the eventual OpenClaw runtime bridge.
If a raw payload is provided, use the real raw->extract->normalize->brief path.
Otherwise fall back to the local service-backed analyzer flow.
"""

from src.analyzers.market_watch import watch_today
from src.analyzers.signal_check import analyze_signal
from src.analyzers.token_analysis import analyze_token
from src.analyzers.wallet_analysis import analyze_wallet
from src.services.runtime_bridge_live_stub import (
    signal_from_raw,
    token_from_raw,
    wallet_from_raw,
    watchtoday_from_raw,
)
from src.services.runtime_payloads import RuntimePayload


def run_token_flow(symbol: str, raw_payload: dict | None = None):
    payload = RuntimePayload(command="token", entity=symbol, raw=raw_payload or {})
    if raw_payload is not None:
        return _brief_from_text(token_from_raw(symbol, raw_payload), f"Token: {symbol}"), payload
    return analyze_token(symbol), payload


def run_signal_flow(token: str, raw_payload: dict | None = None):
    payload = RuntimePayload(command="signal", entity=token, raw=raw_payload or {})
    if raw_payload is not None:
        return _brief_from_text(signal_from_raw(token, raw_payload), f"Signal: {token}"), payload
    return analyze_signal(token), payload


def run_wallet_flow(address: str, raw_payload: dict | None = None):
    payload = RuntimePayload(command="wallet", entity=address, raw=raw_payload or {})
    if raw_payload is not None:
        return _brief_from_text(wallet_from_raw(address, raw_payload), f"Wallet: {address}"), payload
    return analyze_wallet(address), payload


def run_watchtoday_flow(raw_payload: dict | None = None):
    payload = RuntimePayload(command="watchtoday", raw=raw_payload or {})
    if raw_payload is not None:
        return _brief_from_text(watchtoday_from_raw(raw_payload), "Market Watch"), payload
    return watch_today(), payload


def _brief_from_text(formatted: str, entity: str):
    """Return a lightweight object matching the existing test expectations."""

    class _RenderedBrief:
        def __init__(self, entity: str, rendered: str) -> None:
            self.entity = entity
            self.rendered = rendered

    return _RenderedBrief(entity=entity, rendered=formatted)
