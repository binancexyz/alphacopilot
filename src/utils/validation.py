from __future__ import annotations


def looks_like_wallet_address(value: str) -> bool:
    value = value.strip()
    return value.startswith("0x") and len(value) >= 12
