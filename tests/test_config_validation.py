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


def test_config_errors_require_locked_down_auth_outside_development():
    old_env = config.settings.app_env
    old_enabled = config.settings.api_auth_enabled
    old_key = config.settings.api_auth_key
    config.settings.app_env = 'production'
    config.settings.api_auth_enabled = False
    config.settings.api_auth_key = ''
    try:
        errors = config.config_errors('api')
    finally:
        config.settings.app_env = old_env
        config.settings.api_auth_enabled = old_enabled
        config.settings.api_auth_key = old_key
    assert any('API_AUTH_ENABLED=true' in item for item in errors)


def test_config_errors_require_bridge_auth_outside_development():
    old_env = config.settings.app_env
    old_api_key = config.settings.api_auth_key
    old_bridge_key = config.settings.bridge_api_key
    config.settings.app_env = 'production'
    config.settings.api_auth_key = ''
    config.settings.bridge_api_key = ''
    try:
        errors = config.config_errors('bridge')
    finally:
        config.settings.app_env = old_env
        config.settings.api_auth_key = old_api_key
        config.settings.bridge_api_key = old_bridge_key
    assert any('BRIDGE_API_KEY' in item for item in errors)
