from __future__ import annotations

"""
Live runtime bridge stub.

This file exists to make the next implementation phase more concrete.
It does not execute OpenClaw tools directly from this repo yet.
Instead, it defines the shape the runtime-facing bridge should follow.
"""

from src.analyzers.market_watch import watch_today
from src.analyzers.signal_check import analyze_signal
from src.analyzers.token_analysis import analyze_token
from src.analyzers.wallet_analysis import analyze_wallet
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
    brief = analyze_token(symbol)
    return format_brief(brief)


def signal_from_raw(token: str, raw_payload: dict) -> str:
    ctx_dict = extract_signal_context(raw_payload, token)
    ctx = normalize_signal_context(ctx_dict)
    brief = analyze_signal(token)
    return format_brief(brief)


def wallet_from_raw(address: str, raw_payload: dict) -> str:
    ctx_dict = extract_wallet_context(raw_payload, address)
    ctx = normalize_wallet_context(ctx_dict)
    brief = analyze_wallet(address)
    return format_brief(brief)


def watchtoday_from_raw(raw_payload: dict) -> str:
    ctx_dict = extract_watch_today_context(raw_payload)
    ctx = normalize_watch_today_context(ctx_dict)
    brief = watch_today()
    return format_brief(brief)
