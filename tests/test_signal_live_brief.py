from src.analyzers.signal_live_brief import build_signal_brief
from src.models.context import SignalContext


def test_build_signal_brief():
    ctx = SignalContext(
        token="DOGE",
        signal_status="watch",
        trigger_price=0.1,
        current_price=0.11,
        max_gain=45.2,
        volume_24h=1_200_000,
        market_cap=45_000_000,
        smart_money_inflow_usd=250_000,
        supporting_context="Momentum is improving but confirmation is incomplete.",
        audit_flags=[],
        major_risks=["Weak follow-through can turn momentum into noise."],
    )
    brief = build_signal_brief(ctx)
    assert brief.entity == "Signal: DOGE"
    assert brief.signal_quality in {"High", "Medium", "Low"}
    assert brief.conviction is not None
    assert any(tag.name == "Evidence Quality" for tag in brief.risk_tags)
    assert any(tag.name == "Entry Zone" for tag in brief.risk_tags)
    assert any(tag.name == "Invalidation" for tag in brief.risk_tags)
    assert any(tag.name == "Max Gain" for tag in brief.risk_tags)
    assert any(tag.name == "Smart Money Inflow" for tag in brief.risk_tags)
