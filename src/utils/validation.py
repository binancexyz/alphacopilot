from __future__ import annotations

import re

_WALLET_RE = re.compile(r"^0x[0-9a-fA-F]{10,}$")


def looks_like_wallet_address(value: str) -> bool:
    return bool(_WALLET_RE.match(value.strip()))
