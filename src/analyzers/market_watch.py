from __future__ import annotations

from src.analyzers.watchtoday_live_brief import build_watchtoday_brief
from src.models.schemas import AnalysisBrief
from src.services.factory import get_market_data_service
from src.services.normalizers import normalize_watch_today_context


def watch_today() -> AnalysisBrief:
    service = get_market_data_service()
    raw_context = service.get_watch_today_context()
    watch_context = normalize_watch_today_context(raw_context)
    return build_watchtoday_brief(watch_context)
