from __future__ import annotations

"""
Placeholder bridge for future OpenClaw runtime integration.

Intended role:
- receive normalized raw tool outputs collected by OpenClaw
- map them into the Python service / analyzer layer
- keep the product logic reusable outside the runtime shell
"""

from src.services.normalizers import (
    normalize_signal_context,
    normalize_token_context,
    normalize_wallet_context,
    normalize_watch_today_context,
)


def build_token_context(raw_payload: dict):
    return normalize_token_context(raw_payload)


def build_wallet_context(raw_payload: dict):
    return normalize_wallet_context(raw_payload)


def build_watch_today_context(raw_payload: dict):
    return normalize_watch_today_context(raw_payload)


def build_signal_context(raw_payload: dict):
    return normalize_signal_context(raw_payload)
