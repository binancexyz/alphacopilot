from __future__ import annotations

"""
Mapping notes for live Binance Skills Hub integration.

This module is intentionally lightweight for now: it documents the expected
skill-to-context relationship in code so future implementation stays grounded.

Latest assumption update:
- prefer Binance Skills/runtime invocation as the primary integration model
- treat `square-post` as a required publishing/output capability
- treat `spot` as a deferred higher-risk execution capability
"""

TOKEN_SKILLS = [
    "query-token-info",
    "crypto-market-rank",
    "trading-signal",
    "query-token-audit",
]

WALLET_SKILLS = [
    "query-address-info",
    "query-token-info",
    "query-token-audit",
]

WATCH_TODAY_SKILLS = [
    "crypto-market-rank",
    "meme-rush",
    "trading-signal",
]

SIGNAL_SKILLS = [
    "trading-signal",
    "query-token-info",
    "query-token-audit",
]
