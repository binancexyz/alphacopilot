import src.config as config


def test_config_warnings_reports_live_without_base_url():
    old_mode = config.settings.app_mode
    old_base = config.settings.binance_skills_base_url
    config.settings.app_mode = 'live'
    config.settings.binance_skills_base_url = ''
    try:
        warnings = config.config_warnings()
    finally:
        config.settings.app_mode = old_mode
        config.settings.binance_skills_base_url = old_base
    assert any('BINANCE_SKILLS_BASE_URL' in item for item in warnings)
