from __future__ import annotations

from src.analyzers.signal_live_brief import build_signal_brief
from src.models.schemas import AnalysisBrief
from src.services.factory import get_market_data_service
from src.services.normalizers import normalize_signal_context


def analyze_signal(token: str) -> AnalysisBrief:
    service = get_market_data_service()
    raw_context = service.get_signal_context(token)
    signal_context = normalize_signal_context(raw_context)
    return build_signal_brief(signal_context)
