from src.analyzers.token_live_brief import build_token_brief
from src.formatters.brief_formatter import format_brief
from src.models.context import TokenContext


def test_token_render_aligns_active_verdict_with_snapshot_signal():
    brief = build_token_brief(
        TokenContext(
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
    )
    rendered = format_brief(brief)
    assert "Signal: Active follow-through" in rendered



def test_token_render_aligns_late_verdict_with_snapshot_signal():
    brief = build_token_brief(
        TokenContext(
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
            exit_rate=82,
            signal_freshness="FRESH",
            signal_age_hours=0.7,
            audit_gate="ALLOW",
        )
    )
    rendered = format_brief(brief)
    assert "Signal: Active — late setup" in rendered
    assert "Top-10 concentration: 84.0%" in rendered
