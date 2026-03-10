from __future__ import annotations

"""
Template helpers for the eventual OpenClaw runtime bridge.
These do not call live tools yet; they define the shape of the bridge logic.
"""

from src.analyzers.market_watch import watch_today
from src.analyzers.signal_check import analyze_signal
from src.analyzers.token_analysis import analyze_token
from src.analyzers.wallet_analysis import analyze_wallet
from src.services.runtime_payloads import RuntimePayload


def run_token_flow(symbol: str, raw_payload: dict | None = None):
    payload = RuntimePayload(command="token", entity=symbol, raw=raw_payload or {})
    return analyze_token(symbol), payload


def run_signal_flow(token: str, raw_payload: dict | None = None):
    payload = RuntimePayload(command="signal", entity=token, raw=raw_payload or {})
    return analyze_signal(token), payload


def run_wallet_flow(address: str, raw_payload: dict | None = None):
    payload = RuntimePayload(command="wallet", entity=address, raw=raw_payload or {})
    return analyze_wallet(address), payload


def run_watchtoday_flow(raw_payload: dict | None = None):
    payload = RuntimePayload(command="watchtoday", raw=raw_payload or {})
    return watch_today(), payload
