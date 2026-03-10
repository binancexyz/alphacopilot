from __future__ import annotations


def normalize_token_input(raw: str) -> str:
    return raw.strip().upper()


def normalize_wallet_input(raw: str) -> str:
    return raw.strip()
