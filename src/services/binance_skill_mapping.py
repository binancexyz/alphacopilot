from __future__ import annotations

"""
Canonical command-to-skill mapping for live Binance Skills integration.

This module is used both by the bridge layer and by runtime/extractor logic
that needs to understand which skills are expected for a given command.
"""

COMMAND_SKILL_MAP: dict[str, list[str]] = {
    "token": [
        "query-token-info",
        "crypto-market-rank",
        "trading-signal",
        "query-token-audit",
    ],
    "wallet": [
        "query-address-info",
    ],
    "watchtoday": [
        "crypto-market-rank",
        "meme-rush",
        "trading-signal",
    ],
    "signal": [
        "trading-signal",
        "query-token-info",
        "query-token-audit",
    ],
    "audit": [
        "query-token-info",
        "query-token-audit",
    ],
    "meme": [
        "query-token-info",
        "query-token-audit",
        "trading-signal",
        "meme-rush",
        "crypto-market-rank",
    ],
}

OPTIONAL_COMMAND_SKILL_MAP: dict[str, list[str]] = {
    "wallet": [
        "query-token-info",
        "crypto-market-rank",
        "query-token-audit",
    ],
}

TOKEN_SKILLS = COMMAND_SKILL_MAP["token"]
WALLET_SKILLS = COMMAND_SKILL_MAP["wallet"]
WATCH_TODAY_SKILLS = COMMAND_SKILL_MAP["watchtoday"]
SIGNAL_SKILLS = COMMAND_SKILL_MAP["signal"]
AUDIT_SKILLS = COMMAND_SKILL_MAP["audit"]
MEME_SKILLS = COMMAND_SKILL_MAP["meme"]
