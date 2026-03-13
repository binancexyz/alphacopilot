import random

import src.square_diary as square_diary


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
