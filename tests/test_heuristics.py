from src.formatters.heuristics import token_conviction, token_signal_quality
from src.models.context import TokenContext


def test_token_signal_quality_high():
    ctx = TokenContext(
        symbol="BNB",
        display_name="BNB",
        liquidity=1000,
        holders=100,
        signal_status="watch",
        audit_flags=[],
        major_risks=[],
    )
    assert token_signal_quality(ctx) == "High"


def test_token_conviction_low_when_risks_high():
    ctx = TokenContext(
        symbol="DOGE",
        display_name="DOGE",
        liquidity=1000,
        holders=100,
        signal_status="watch",
        audit_flags=["owner privileges"],
        major_risks=["fragile setup", "weak follow-through", "high volatility"],
    )
    assert token_conviction(ctx) == "Low"
