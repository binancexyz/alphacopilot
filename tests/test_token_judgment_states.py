from src.analyzers.token_live_brief import build_token_brief
from src.models.context import TokenContext


def test_token_brief_marks_active_supportive_structure():
    ctx = TokenContext(
        symbol="BNB",
        display_name="BNB",
        price=600,
        liquidity=120_000_000,
        holders=120000,
        top_holder_concentration_pct=34,
        market_rank_context="Large-cap with strong ecosystem relevance.",
        signal_status="triggered",
        signal_trigger_context="Signal is active.",
        smart_money_count=5,
        exit_rate=18,
        signal_freshness="FRESH",
        signal_age_hours=0.5,
        audit_gate="ALLOW",
    )
    brief = build_token_brief(ctx)
    assert brief.quick_verdict == "Active setup. Structure is supportive."
    assert brief.conviction == "High"



def test_token_brief_marks_active_but_ownership_risky():
    ctx = TokenContext(
        symbol="DOGE",
        display_name="DOGE",
        price=0.1,
        liquidity=25_000_000,
        holders=8000,
        top_holder_concentration_pct=84,
        market_rank_context="Visible on the board.",
        signal_status="triggered",
        signal_trigger_context="Signal is active.",
        smart_money_count=4,
        exit_rate=20,
        signal_freshness="FRESH",
        signal_age_hours=0.7,
        audit_gate="ALLOW",
    )
    brief = build_token_brief(ctx)
    assert brief.quick_verdict == "Active setup. Ownership risk is still heavy."
    assert any("Top-holder concentration" in risk for risk in brief.top_risks)



def test_token_brief_marks_late_setup_when_exit_pressure_is_high():
    ctx = TokenContext(
        symbol="DOGE",
        display_name="DOGE",
        price=0.1,
        liquidity=15_000_000,
        holders=5000,
        top_holder_concentration_pct=52,
        market_rank_context="Visible on the board.",
        signal_status="triggered",
        signal_trigger_context="Signal is active.",
        smart_money_count=5,
        exit_rate=78,
        signal_freshness="FRESH",
        signal_age_hours=0.9,
        audit_gate="ALLOW",
    )
    brief = build_token_brief(ctx)
    assert brief.quick_verdict == "Active but late. Exit pressure is rising."



def test_token_brief_marks_stale_setup_when_timing_is_old():
    ctx = TokenContext(
        symbol="DOGE",
        display_name="DOGE",
        price=0.1,
        liquidity=15_000_000,
        holders=5000,
        top_holder_concentration_pct=40,
        market_rank_context="Visible on the board.",
        signal_status="watch",
        signal_trigger_context="Signal exists.",
        smart_money_count=2,
        exit_rate=15,
        signal_freshness="STALE",
        signal_age_hours=20,
        audit_gate="ALLOW",
    )
    brief = build_token_brief(ctx)
    assert brief.quick_verdict == "Stale setup. Fresh confirmation needed."



def test_token_brief_marks_blocked_setup_when_audit_blocks():
    ctx = TokenContext(
        symbol="DOGE",
        display_name="DOGE",
        audit_gate="BLOCK",
        blocked_reason="Critical audit flags detected.",
    )
    brief = build_token_brief(ctx)
    assert brief.quick_verdict == "Blocked. Audit risk is too high."
