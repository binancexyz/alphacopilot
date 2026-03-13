from src.formatters.heuristics import signal_quality_from_signal
from src.models.context import SignalContext


def test_signal_quality_triggered_without_context_is_not_auto_high():
    ctx = SignalContext(token="BNB", signal_status="triggered", audit_flags=[])
    assert signal_quality_from_signal(ctx) == "Medium"


def test_signal_quality_watch_without_context_stays_low():
    ctx = SignalContext(token="DOGE", signal_status="watch", audit_flags=[])
    assert signal_quality_from_signal(ctx) == "Low"
