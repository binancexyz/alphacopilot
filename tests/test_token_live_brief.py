from src.analyzers.token_live_brief import build_token_brief
from src.models.context import TokenContext


def test_build_token_brief():
    ctx = TokenContext(
        symbol="BNB",
        display_name="BNB",
        liquidity=1200,
        holders=500,
        market_rank_context="large-cap with strong ecosystem relevance",
        signal_status="watch",
        signal_trigger_context="Momentum is improving but still needs confirmation.",
        audit_flags=[],
        major_risks=["Signal may weaken if volume does not confirm."],
    )
    brief = build_token_brief(ctx)
    assert brief.entity == "Token: BNB"
    assert brief.signal_quality in {"High", "Medium", "Low"}
    assert brief.conviction is not None
