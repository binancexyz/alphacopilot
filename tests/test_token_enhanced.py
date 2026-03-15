from src.analyzers.token_live_brief import (
    _compute_momentum_score,
    _relative_strength_note,
    _volume_trend_note,
    build_token_brief,
)
from src.models.context import TokenContext


def test_momentum_score_computation():
    ctx = TokenContext(
        symbol="BTC",
        display_name="Bitcoin",
        pct_change_5m=0.5,
        pct_change_1h=1.5,
        pct_change_4h=3.0,
        pct_change_24h=5.0,
    )
    score = _compute_momentum_score(ctx)
    # 0.5*0.1 + 1.5*0.25 + 3.0*0.35 + 5.0*0.3 = 0.05 + 0.375 + 1.05 + 1.5 = 2.975
    assert abs(score - 2.98) < 0.1
    print("PASS test_momentum_score_computation")


def test_volume_trend_spike_detection():
    ctx = TokenContext(
        symbol="DOGE",
        display_name="Dogecoin",
        volume_5m=1_000_000,
        volume_1h=4_000_000,
    )
    trend = _volume_trend_note(ctx)
    # 5m * 12 = 12M vs 1h = 4M → ratio 3.0 → spike
    assert trend == "spike"
    print("PASS test_volume_trend_spike_detection")


def test_volume_trend_decreasing():
    ctx = TokenContext(
        symbol="ADA",
        display_name="Cardano",
        volume_5m=100_000,
        volume_1h=5_000_000,
    )
    trend = _volume_trend_note(ctx)
    # 5m * 12 = 1.2M vs 1h = 5M → ratio 0.24 → decreasing
    assert trend == "decreasing"
    print("PASS test_volume_trend_decreasing")


def test_volume_trend_returns_existing():
    ctx = TokenContext(
        symbol="SOL",
        display_name="Solana",
        volume_trend="increasing",
    )
    trend = _volume_trend_note(ctx)
    assert trend == "increasing"
    print("PASS test_volume_trend_returns_existing")


def test_relative_strength_outperformance():
    ctx = TokenContext(
        symbol="BNB",
        display_name="BNB",
        pct_change_24h=8.0,
        btc_change_24h=1.0,
    )
    note = _relative_strength_note(ctx)
    assert "outperformance" in note.lower()
    print("PASS test_relative_strength_outperformance")


def test_relative_strength_underperformance():
    ctx = TokenContext(
        symbol="ETH",
        display_name="Ethereum",
        pct_change_24h=-2.0,
        btc_change_24h=3.0,
    )
    note = _relative_strength_note(ctx)
    assert "underperform" in note.lower()
    print("PASS test_relative_strength_underperformance")


def test_token_brief_includes_momentum_and_volume_tags():
    ctx = TokenContext(
        symbol="BTC",
        display_name="Bitcoin",
        price=65000.0,
        liquidity=100_000_000,
        holders=50000,
        signal_status="bullish",
        signal_freshness="FRESH",
        signal_age_hours=0.5,
        smart_money_count=5,
        pct_change_5m=0.3,
        pct_change_1h=1.0,
        pct_change_4h=2.5,
        pct_change_24h=4.0,
        volume_5m=500_000,
        volume_1h=2_000_000,
        btc_change_24h=1.0,
    )
    brief = build_token_brief(ctx)
    tag_names = [t.name for t in brief.risk_tags]
    assert "Momentum Score" in tag_names
    assert "Volume Trend" in tag_names
    assert "Relative Strength" in tag_names
    print("PASS test_token_brief_includes_momentum_and_volume_tags")


def test_token_brief_includes_support_resistance():
    ctx = TokenContext(
        symbol="ETH",
        display_name="Ethereum",
        price=3500.0,
        support_level=3200.0,
        resistance_level=3800.0,
        signal_status="watch",
    )
    brief = build_token_brief(ctx)
    tag_names = [t.name for t in brief.risk_tags]
    assert "Support" in tag_names
    assert "Resistance" in tag_names
    support_tag = next(t for t in brief.risk_tags if t.name == "Support")
    assert "3,200" in support_tag.note
    print("PASS test_token_brief_includes_support_resistance")
