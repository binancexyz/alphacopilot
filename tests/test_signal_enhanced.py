from src.analyzers.signal_live_brief import build_signal_brief
from src.models.context import SignalContext


def test_signal_dynamic_entry_zone_uses_atr():
    ctx = SignalContext(
        token="BTC",
        signal_status="triggered",
        trigger_price=65000.0,
        current_price=65200.0,
        price_high_24h=67000.0,
        price_low_24h=63000.0,
        signal_freshness="FRESH",
        signal_age_hours=0.5,
        smart_money_count=3,
        liquidity=50_000_000,
        volume_24h=1_000_000_000,
    )
    brief = build_signal_brief(ctx)
    entry_tag = next((t for t in brief.risk_tags if t.name == "Entry Zone"), None)
    assert entry_tag is not None
    # With high/low of 67000/63000, ATR range is 4000/65000 ≈ 6.15%, * 1.5 ≈ 9.2%
    # So zone should be wider than the default ±1%
    assert "ATR-adjusted" in entry_tag.note
    # The zone should NOT be the fixed ±1% (which would be $64350 – $65650)
    assert "$64,350" not in entry_tag.note
    print("PASS test_signal_dynamic_entry_zone_uses_atr")


def test_signal_fallback_entry_zone_when_no_atr_data():
    ctx = SignalContext(
        token="DOGE",
        signal_status="watch",
        trigger_price=0.15,
        current_price=0.14,
    )
    brief = build_signal_brief(ctx)
    entry_tag = next((t for t in brief.risk_tags if t.name == "Entry Zone"), None)
    assert entry_tag is not None
    # No high/low data, so should use fallback ±1%
    assert "ATR-adjusted" not in entry_tag.note
    print("PASS test_signal_fallback_entry_zone_when_no_atr_data")


def test_signal_risk_reward_ratio():
    ctx = SignalContext(
        token="ETH",
        signal_status="triggered",
        trigger_price=3500.0,
        current_price=3520.0,
        price_high_24h=3700.0,
        price_low_24h=3400.0,
        signal_freshness="FRESH",
        signal_age_hours=0.3,
        smart_money_count=2,
        liquidity=10_000_000,
    )
    brief = build_signal_brief(ctx)
    rr_tag = next((t for t in brief.risk_tags if t.name == "Risk/Reward"), None)
    assert rr_tag is not None
    assert ":1" in rr_tag.note
    print("PASS test_signal_risk_reward_ratio")


def test_signal_take_profit_zone():
    ctx = SignalContext(
        token="SOL",
        signal_status="triggered",
        trigger_price=150.0,
        current_price=155.0,
        price_high_24h=165.0,
        price_low_24h=145.0,
        signal_freshness="FRESH",
        signal_age_hours=1.0,
        smart_money_count=1,
    )
    brief = build_signal_brief(ctx)
    tp_tag = next((t for t in brief.risk_tags if t.name == "Take-Profit Zone"), None)
    assert tp_tag is not None
    assert "165" in tp_tag.note
    print("PASS test_signal_take_profit_zone")


def test_signal_btc_drag_detection():
    ctx = SignalContext(
        token="DOGE",
        signal_status="watch",
        trigger_price=0.15,
        current_price=0.14,
        pct_change_24h=-6.0,
        btc_change_24h=-3.0,
    )
    brief = build_signal_brief(ctx)
    drag_tag = next((t for t in brief.risk_tags if t.name == "BTC Drag"), None)
    assert drag_tag is not None, f"Expected BTC Drag tag but got: {[t.name for t in brief.risk_tags]}"
    assert "dragging" in drag_tag.note.lower()
    print("PASS test_signal_btc_drag_detection")


def test_signal_relative_strength_outperforming():
    ctx = SignalContext(
        token="BNB",
        signal_status="triggered",
        trigger_price=600.0,
        current_price=620.0,
        pct_change_24h=5.0,
        btc_change_24h=-2.0,
    )
    brief = build_signal_brief(ctx)
    rs_tag = next((t for t in brief.risk_tags if t.name == "Relative Strength"), None)
    assert rs_tag is not None, f"Expected Relative Strength tag but got: {[t.name for t in brief.risk_tags]}"
    assert "outperforming" in rs_tag.note.lower()
    print("PASS test_signal_relative_strength_outperforming")


def test_signal_volume_trend_tag():
    ctx = SignalContext(
        token="ADA",
        signal_status="watch",
        trigger_price=0.5,
        current_price=0.49,
        volume_24h=500_000_000,
        volume_trend="increasing",
    )
    brief = build_signal_brief(ctx)
    vol_tag = next((t for t in brief.risk_tags if t.name == "Volume Trend"), None)
    assert vol_tag is not None
    assert "increasing" in vol_tag.note.lower()
    print("PASS test_signal_volume_trend_tag")
