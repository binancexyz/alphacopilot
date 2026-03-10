from src.analyzers.signal_live_brief import build_signal_brief
from src.models.context import SignalContext


def test_build_signal_brief():
    ctx = SignalContext(
        token="DOGE",
        signal_status="watch",
        supporting_context="Momentum is improving but confirmation is incomplete.",
        audit_flags=[],
        major_risks=["Weak follow-through can turn momentum into noise."],
    )
    brief = build_signal_brief(ctx)
    assert brief.entity == "Signal: DOGE"
    assert brief.signal_quality in {"High", "Medium", "Low"}
    assert brief.conviction is not None
