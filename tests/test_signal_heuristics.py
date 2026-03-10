from src.formatters.heuristics import signal_quality_from_signal
from src.models.context import SignalContext


def test_signal_quality_high_without_audit_flags():
    ctx = SignalContext(token="BNB", signal_status="triggered", audit_flags=[])
    assert signal_quality_from_signal(ctx) == "High"


def test_signal_quality_medium_when_watch():
    ctx = SignalContext(token="DOGE", signal_status="watch", audit_flags=[])
    assert signal_quality_from_signal(ctx) == "Medium"
