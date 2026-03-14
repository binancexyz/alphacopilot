from __future__ import annotations

"""
Canonical command-to-skill mapping for live Binance Skills integration.

This module is used both by the bridge layer and by runtime/extractor logic
that needs to understand which skills are expected for a given command.
"""

COMMAND_SKILL_MAP: dict[str, list[str]] = {
    "alpha": [
        "alpha",
        "query-token-info",
        "query-token-audit",
    ],
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
        "crypto-market-rank",
        "derivatives-trading-usds-futures",
    ],
    "audit": [
        "query-token-info",
        "query-token-audit",
        "trading-signal",
    ],
    "meme": [
        "query-token-info",
        "query-token-audit",
        "trading-signal",
        "meme-rush",
        "crypto-market-rank",
    ],
    "futures": [
        "derivatives-trading-usds-futures",
        "query-token-info",
    ],
    "portfolio": [
        "assets",
        "margin-trading",
    ]
}

OPTIONAL_COMMAND_SKILL_MAP: dict[str, list[str]] = {
    "wallet": [
        "query-token-info",
        "crypto-market-rank",
        "query-token-audit",
    ],
    "token": [
        "alpha",
        "spot",
        "derivatives-trading-usds-futures",
        "meme-rush",
    ],
    "signal": [
        "crypto-market-rank",
        "derivatives-trading-usds-futures",
    ],
    "watchtoday": [
        "derivatives-trading-usds-futures",
    ],
}

ALPHA_SKILLS = COMMAND_SKILL_MAP["alpha"]
TOKEN_SKILLS = COMMAND_SKILL_MAP["token"]
WALLET_SKILLS = COMMAND_SKILL_MAP["wallet"]
WATCH_TODAY_SKILLS = COMMAND_SKILL_MAP["watchtoday"]
SIGNAL_SKILLS = COMMAND_SKILL_MAP["signal"]
AUDIT_SKILLS = COMMAND_SKILL_MAP["audit"]
MEME_SKILLS = COMMAND_SKILL_MAP["meme"]
FUTURES_SKILLS = COMMAND_SKILL_MAP["futures"]
PORTFOLIO_SKILLS = COMMAND_SKILL_MAP["portfolio"]
