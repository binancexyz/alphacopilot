from pathlib import Path

import src.services.portfolio_history as portfolio_history


def test_describe_delta_detects_material_changes():
    previous = {
        'total_value': 1000.0,
        'stable_pct': 20.0,
        'concentration': 30.0,
        'priced_assets': [
            {'asset': 'USDT', 'usd_value': 200.0},
            {'asset': 'BNB', 'usd_value': 800.0},
        ],
    }
    current = {
        'total_value': 1200.0,
        'stable_pct': 40.0,
        'concentration': 45.0,
        'priced_assets': [
            {'asset': 'USDT', 'usd_value': 480.0},
            {'asset': 'BNB', 'usd_value': 520.0},
            {'asset': 'ETH', 'usd_value': 200.0},
        ],
    }
    summary, changes = portfolio_history.describe_delta(previous, current)
    assert 'Estimated visible value is up' in summary
    assert any('Stablecoin share is higher' in item for item in changes)
    assert any('New priced assets' in item for item in changes)


def test_append_and_load_history(tmp_path: Path):
    old_path = portfolio_history.HISTORY_PATH
    portfolio_history.HISTORY_PATH = tmp_path / 'portfolio_history.json'
    if portfolio_history.HISTORY_PATH.exists():
        portfolio_history.HISTORY_PATH.unlink()
    try:
        portfolio_history.append_snapshot({'total_value': 1.0, 'priced_assets': []})
        history = portfolio_history.load_history()
    finally:
        portfolio_history.HISTORY_PATH = old_path
    assert len(history) == 1
    assert history[0]['total_value'] == 1.0
