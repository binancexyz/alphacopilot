from src.formatters.heuristics import signal_quality_from_signal
from src.models.context import SignalContext


def test_signal_quality_triggered_without_context_is_not_auto_high():
    ctx = SignalContext(token="BNB", signal_status="triggered", audit_flags=[])
    assert signal_quality_from_signal(ctx) == "Medium"


def test_signal_quality_watch_without_context_stays_low():
    ctx = SignalContext(token="DOGE", signal_status="watch", audit_flags=[])
    assert signal_quality_from_signal(ctx) == "Low"


def test_signal_quality_penalizes_thin_and_crowded_futures_setup():
    ctx = SignalContext(
        token="DOGE",
        signal_status="triggered",
        trigger_price=0.10,
        current_price=0.11,
        smart_money_count=4,
        signal_freshness="FRESH",
        liquidity=500_000,
        funding_rate=0.002,
        long_short_ratio=3.0,
        audit_gate="ALLOW",
    )
    assert signal_quality_from_signal(ctx) == "Medium"
