from __future__ import annotations

"""
Live runtime bridge stub.

This file exists to make the next implementation phase more concrete.
It does not execute OpenClaw tools directly from this repo yet.
Instead, it defines the shape the runtime-facing bridge should follow.
"""

from src.analyzers.signal_live_brief import build_signal_brief
from src.analyzers.token_live_brief import build_token_brief
from src.analyzers.wallet_live_brief import build_wallet_brief
from src.analyzers.watchtoday_live_brief import build_watchtoday_brief
from src.formatters.brief_formatter import format_brief
from src.services.live_extractors import (
    extract_signal_context,
    extract_token_context,
    extract_wallet_context,
    extract_watch_today_context,
)
from src.services.normalizers import (
    normalize_signal_context,
    normalize_token_context,
    normalize_wallet_context,
    normalize_watch_today_context,
)


def token_from_raw(symbol: str, raw_payload: dict) -> str:
    ctx_dict = extract_token_context(raw_payload, symbol)
    ctx = normalize_token_context(ctx_dict)
    brief = build_token_brief(ctx)
    return format_brief(brief)


def signal_from_raw(token: str, raw_payload: dict) -> str:
    ctx_dict = extract_signal_context(raw_payload, token)
    ctx = normalize_signal_context(ctx_dict)
    brief = build_signal_brief(ctx)
    return format_brief(brief)


def wallet_from_raw(address: str, raw_payload: dict) -> str:
    ctx_dict = extract_wallet_context(raw_payload, address)
    ctx = normalize_wallet_context(ctx_dict)
    brief = build_wallet_brief(ctx)
    return format_brief(brief)


def watchtoday_from_raw(raw_payload: dict) -> str:
    ctx_dict = extract_watch_today_context(raw_payload)
    ctx = normalize_watch_today_context(ctx_dict)
    brief = build_watchtoday_brief(ctx)
    return format_brief(brief)
