from __future__ import annotations

from src.analyzers.wallet_live_brief import build_wallet_brief
from src.services.factory import get_market_data_service
from src.services.normalizers import normalize_wallet_context


def analyze_wallet(address: str):
    service = get_market_data_service()
    raw_context = service.get_wallet_context(address)
    wallet_context = normalize_wallet_context(raw_context)
    return build_wallet_brief(wallet_context)
