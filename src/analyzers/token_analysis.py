from __future__ import annotations

from src.analyzers.token_live_brief import build_token_brief
from src.services.factory import get_market_data_service
from src.services.normalizers import normalize_token_context


def analyze_token(symbol: str):
    service = get_market_data_service()
    raw_context = service.get_token_context(symbol)
    token_context = normalize_token_context(raw_context)
    return build_token_brief(token_context)
