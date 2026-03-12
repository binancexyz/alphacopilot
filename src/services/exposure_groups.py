from __future__ import annotations

from typing import Iterable

STABLES = {"USDT", "USDC", "BUSD", "FDUSD", "TUSD", "USDP", "DAI"}
MAJORS = {"BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "TRX", "TON", "AVAX", "LINK", "BCH"}
MEME = {"DOGS", "PENGU", "1000CAT", "BARD", "NOT"}
AI = {"WLD", "VANA", "SXT"}
INFRA = {"ASTER", "ZKC", "WAL", "OPEN", "TOWNS", "JASMY"}


def classify_asset(asset: str) -> str:
    sym = asset.upper().strip()
    if sym in STABLES:
        return "Stablecoins"
    if sym in MAJORS:
        return "Majors"
    if sym in MEME:
        return "Meme"
    if sym in AI:
        return "AI"
    if sym in INFRA:
        return "Infra"
    return "Other"


def top_groups(priced_assets: Iterable[dict]) -> list[tuple[str, float]]:
    buckets: dict[str, float] = {}
    total = 0.0
    for item in priced_assets:
        asset = str(item.get("asset") or "")
        value = float(item.get("usd_value") or 0)
        if value <= 0:
            continue
        total += value
        group = classify_asset(asset)
        buckets[group] = buckets.get(group, 0.0) + value
    if total <= 0:
        return []
    ranked = sorted(((name, value / total * 100) for name, value in buckets.items()), key=lambda x: x[1], reverse=True)
    return ranked
