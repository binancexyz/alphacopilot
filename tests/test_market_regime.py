from src.analyzers.watchtoday_live_brief import _detect_market_regime, build_watchtoday_brief
from src.models.context import WatchTodayContext


def test_market_regime_trending_up():
    ctx = WatchTodayContext(
        btc_change_24h=4.5,
        strongest_signals=["BTC strength"],
    )
    regime = _detect_market_regime(ctx)
    assert regime == "trending-up"
    print("PASS test_market_regime_trending_up")


def test_market_regime_trending_down():
    ctx = WatchTodayContext(
        btc_change_24h=-4.0,
        strongest_signals=["BTC weakness"],
    )
    regime = _detect_market_regime(ctx)
    assert regime == "trending-down"
    print("PASS test_market_regime_trending_down")


def test_market_regime_volatile():
    ctx = WatchTodayContext(
        btc_change_24h=6.0,
    )
    regime = _detect_market_regime(ctx)
    assert regime == "volatile"
    print("PASS test_market_regime_volatile")


def test_market_regime_ranging():
    ctx = WatchTodayContext(
        btc_change_24h=0.3,
        strongest_signals=[],
    )
    regime = _detect_market_regime(ctx)
    assert regime == "ranging"
    print("PASS test_market_regime_ranging")


def test_market_regime_squeeze():
    ctx = WatchTodayContext(
        btc_change_24h=1.0,
        futures_sentiment=["BTC squeeze risk building"],
    )
    regime = _detect_market_regime(ctx)
    assert regime == "squeeze"
    print("PASS test_market_regime_squeeze")


def test_market_regime_uses_existing():
    ctx = WatchTodayContext(
        market_regime="custom-regime",
    )
    regime = _detect_market_regime(ctx)
    assert regime == "custom-regime"
    print("PASS test_market_regime_uses_existing")


def test_watchtoday_brief_includes_regime_tag():
    ctx = WatchTodayContext(
        top_narratives=["AI", "L2"],
        strongest_signals=["BTC", "ETH"],
        btc_change_24h=4.0,
    )
    brief = build_watchtoday_brief(ctx)
    tag_names = [t.name for t in brief.risk_tags]
    assert "Market Regime" in tag_names
    regime_tag = next(t for t in brief.risk_tags if t.name == "Market Regime")
    assert "trending" in regime_tag.note.lower()
    print("PASS test_watchtoday_brief_includes_regime_tag")


def test_watchtoday_brief_includes_btc_tag():
    ctx = WatchTodayContext(
        btc_change_24h=-3.5,
        top_narratives=["AI"],
        strongest_signals=["SOL"],
    )
    brief = build_watchtoday_brief(ctx)
    tag_names = [t.name for t in brief.risk_tags]
    assert "BTC 24h" in tag_names
    btc_tag = next(t for t in brief.risk_tags if t.name == "BTC 24h")
    assert "-3.5" in btc_tag.note
    print("PASS test_watchtoday_brief_includes_btc_tag")
