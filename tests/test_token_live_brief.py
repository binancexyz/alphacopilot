from src.analyzers.token_live_brief import build_token_brief
from src.models.context import TokenContext


def test_build_token_brief():
    ctx = TokenContext(
        symbol="BNB",
        display_name="BNB",
        liquidity=1200,
        holders=500,
        volume_24h=1_200_000,
        market_cap=45_000_000,
        price_low_24h=595.0,
        price_high_24h=625.0,
        market_rank_context="large-cap with strong ecosystem relevance",
        signal_status="watch",
        signal_trigger_context="Momentum is improving but still needs confirmation.",
        buy_sell_ratio=0.63,
        pct_change_5m=1.2,
        pct_change_1h=3.4,
        pct_change_4h=5.6,
        kol_holders=8,
        kol_holding_pct=4.5,
        pro_holders=3,
        pro_holding_pct=2.2,
        audit_flags=[],
        major_risks=["Signal may weaken if volume does not confirm."],
    )
    brief = build_token_brief(ctx)
    assert brief.entity == "Token: BNB"
    assert brief.signal_quality in {"High", "Medium", "Low"}
    assert brief.conviction is not None
    assert any(tag.name == "Evidence Quality" for tag in brief.risk_tags)
    assert any(tag.name == "Market Data" for tag in brief.risk_tags)
    assert any(tag.name == "Buy/Sell Pressure" for tag in brief.risk_tags)
    assert any(tag.name == "Holder Quality" for tag in brief.risk_tags)
    assert any(tag.name == "Momentum" for tag in brief.risk_tags)
