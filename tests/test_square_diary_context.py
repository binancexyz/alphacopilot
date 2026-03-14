import random

import src.square_diary as square_diary
from src.models.context import WatchTodayContext


def test_contextual_market_line_can_use_market_tone():
    old_fetch = square_diary.fetch_market_tone
    try:
        square_diary.fetch_market_tone = lambda config: 'The board still looks selective tonight: strength exists, but only in a few lanes.'
        line = square_diary.contextual_market_line({'market_focus': ['BNB', 'BTC']}, 'crypto market structure', 'market')
    finally:
        square_diary.fetch_market_tone = old_fetch
    assert 'selective tonight' in line


def test_contextual_builder_line_can_use_posture_note():
    old_posture = square_diary.fetch_posture_note
    old_state = random.getstate()
    try:
        random.seed(42)
        square_diary.fetch_posture_note = lambda: 'The current posture still looks defensive, so quality matters more than volume.'
        line = square_diary.contextual_builder_line('signal and risk', 'Make market and risk posture-aware', 'builder')
    finally:
        square_diary.fetch_posture_note = old_posture
        random.setstate(old_state)
    assert 'defensive' in line


def test_choose_morning_mode_prefers_signal_then_narrative():
    signal_ctx = WatchTodayContext(
        strongest_signals=["BNB: BUY (active)", "DOGE: BUY (active)", "SOL: BUY (active)"],
        smart_money_flow=["BNB inflow"],
        top_narratives=["AI", "L2"],
    )
    narrative_ctx = WatchTodayContext(
        top_narratives=["AI", "meme rotation", "L2"],
        strongest_signals=["BNB: BUY (active)"],
    )
    quiet_ctx = WatchTodayContext(
        top_narratives=["AI"],
        strongest_signals=["BNB: BUY (active)"],
    )

    assert square_diary.choose_morning_mode(signal_ctx) == "signal"
    assert square_diary.choose_morning_mode(narrative_ctx) == "narrative"
    assert square_diary.choose_morning_mode(quiet_ctx) == "opportunity"


def test_fetch_morning_market_snapshot_returns_structured_lines():
    class DummyService:
        def get_watch_today_context(self):
            return {
                "top_narratives": ["AI", "meme rotation", "L2"],
                "strongest_signals": ["DOGE: BUY (active)", "BNB: BUY (active)", "SOL: BUY (watch)"],
                "smart_money_flow": ["DOGE inflow", "BNB inflow"],
                "social_hype": ["L2 chatter"],
                "futures_sentiment": ["BTC funding +0.0200% (bearish)", "SOL funding -0.0100% (bullish)"],
                "top_traders": ["0x1234…5678 — PnL $50K — WR 85%"],
            }

    old_service = square_diary.get_market_data_service
    try:
        square_diary.get_market_data_service = lambda: DummyService()
        snapshot = square_diary.fetch_morning_market_snapshot({"market_focus": ["BNB", "BTC"]})
    finally:
        square_diary.get_market_data_service = old_service

    assert snapshot["market_snapshot"]
    assert snapshot["top_setup"]
    assert snapshot["signal_board"]
    assert snapshot["smart_money"]
    assert snapshot["narrative_heat"]
    assert snapshot["futures_note"]
    assert all(len(value) <= 120 for value in snapshot.values() if value)


def test_build_morning_diary_post_uses_market_snapshot_mode():
    class DummyService:
        def get_watch_today_context(self):
            return {
                "top_narratives": ["AI", "meme rotation", "L2"],
                "strongest_signals": ["DOGE: BUY (active)", "BNB: BUY (active)", "SOL: BUY (watch)"],
                "smart_money_flow": ["DOGE inflow", "BNB inflow"],
                "social_hype": ["L2 chatter"],
                "futures_sentiment": ["BTC funding +0.0200% (bearish)"],
            }

    old_service = square_diary.get_market_data_service
    old_posture = square_diary.fetch_posture_note
    old_state = random.getstate()
    state = {
        "recent_hooks": [],
        "recent_lines": [],
        "recent_posts": [],
        "recent_topics": [],
        "recent_ctas": [],
        "recent_series": [],
        "recent_hook_types": [],
    }
    try:
        random.seed(7)
        square_diary.get_market_data_service = lambda: DummyService()
        square_diary.fetch_posture_note = lambda: "The current posture is mixed, which keeps selectivity useful."
        text, meta = square_diary.build_morning_diary_post(
            {"market_focus": ["BNB", "BTC"], "custom_lines": []},
            state,
            "crypto market structure",
            "Clawbot Journal",
            "Morning diary: keep the read clean.",
            "curiosity",
        )
    finally:
        square_diary.get_market_data_service = old_service
        square_diary.fetch_posture_note = old_posture
        random.setstate(old_state)

    assert "Signal board shows" in text
    assert "Smart money is visible" in text
    assert "Futures tone:" in text
    assert meta["slot"] == "morning-diary"
    assert "mode=signal" in meta["voice"]


def test_build_night_diary_post_includes_market_wrap_and_futures():
    old_wrap = square_diary.fetch_night_market_wrap
    old_mode = square_diary.choose_night_mode
    old_market = square_diary.contextual_market_line
    old_posture = square_diary.fetch_posture_note
    old_state = random.getstate()
    state = {
        "recent_hooks": [],
        "recent_lines": [],
        "recent_posts": [],
        "recent_topics": [],
        "recent_ctas": [],
        "recent_series": [],
        "recent_hook_types": [],
    }
    try:
        random.seed(11)
        square_diary.fetch_night_market_wrap = lambda config: {
            "market_snapshot": "Today's board showed 3 signals and 2 trending names. Smart money was active.",
            "top_setup": "Strongest setup of the day was DOGE. Follow-through still looks real.",
            "futures_note": "Futures tone: BTC funding +0.0200% (bearish).",
        }
        square_diary.choose_night_mode = lambda topic, commit_line: "market"
        square_diary.contextual_market_line = lambda config, topic, mode="market": "Into the close, confirmation still mattered."
        square_diary.fetch_posture_note = lambda: ""
        text, meta = square_diary.build_night_diary_post(
            {"custom_lines": []},
            state,
            "crypto market structure",
            "Night Wrap",
            "Night diary: keep the board honest.",
            "lesson",
        )
    finally:
        square_diary.fetch_night_market_wrap = old_wrap
        square_diary.choose_night_mode = old_mode
        square_diary.contextual_market_line = old_market
        square_diary.fetch_posture_note = old_posture
        random.setstate(old_state)

    assert "Today's board showed 3 signals" in text
    assert "Futures tone: BTC funding +0.0200% (bearish)" in text
    assert meta["slot"] == "night-diary"
    assert "mode=market" in meta["voice"]
