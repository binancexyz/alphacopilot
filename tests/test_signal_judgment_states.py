from src.analyzers.signal_live_brief import build_signal_brief
from src.models.context import SignalContext
from src.formatters.heuristics import signal_quality_from_signal


def test_signal_quality_high_for_fresh_trigger_holding_setup():
    ctx = SignalContext(
        token="DOGE",
        signal_status="triggered",
        trigger_price=0.10,
        current_price=0.11,
        smart_money_count=4,
        signal_freshness="FRESH",
        signal_age_hours=0.6,
        exit_rate=18,
        audit_gate="ALLOW",
    )
    assert signal_quality_from_signal(ctx) == "High"
    brief = build_signal_brief(ctx)
    assert brief.quick_verdict == "Active setup. Trigger is holding."
    assert brief.conviction == "High"



def test_signal_brief_marks_late_setup_when_exit_pressure_is_high():
    ctx = SignalContext(
        token="DOGE",
        signal_status="triggered",
        trigger_price=0.10,
        current_price=0.12,
        smart_money_count=5,
        signal_freshness="FRESH",
        signal_age_hours=0.8,
        exit_rate=82,
        audit_gate="ALLOW",
    )
    brief = build_signal_brief(ctx)
    assert brief.quick_verdict == "Active but late. Exit pressure is high."
    assert any("Late setup" in risk for risk in brief.top_risks)



def test_signal_brief_marks_stale_setup_even_if_signal_exists():
    ctx = SignalContext(
        token="DOGE",
        signal_status="watch",
        smart_money_count=0,
        signal_freshness="STALE",
        signal_age_hours=30.0,
        exit_rate=20,
        audit_gate="ALLOW",
    )
    brief = build_signal_brief(ctx)
    assert brief.quick_verdict == "Stale setup. Fresh trigger needed."
    assert any("stale" in risk.lower() for risk in brief.top_risks)



def test_signal_brief_marks_early_setup_below_trigger():
    ctx = SignalContext(
        token="DOGE",
        signal_status="watch",
        trigger_price=0.10,
        current_price=0.09,
        smart_money_count=3,
        signal_freshness="FRESH",
        signal_age_hours=1.2,
        exit_rate=15,
        audit_gate="ALLOW",
    )
    brief = build_signal_brief(ctx)
    assert brief.quick_verdict == "Early setup. Trigger still needs reclaim."
    assert any("below the trigger zone" in risk for risk in brief.top_risks)



def test_signal_quality_blocked_when_audit_gate_blocks():
    ctx = SignalContext(token="DOGE", signal_status="triggered", audit_gate="BLOCK", blocked_reason="Critical audit flags detected.")
    assert signal_quality_from_signal(ctx) == "Blocked"
    brief = build_signal_brief(ctx)
    assert brief.quick_verdict == "Blocked. Audit risk too high."
