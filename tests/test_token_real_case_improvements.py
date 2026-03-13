import src.analyzers.token_analysis as token_analysis
from src.formatters.brief_formatter import format_brief


class DummyService:
    def get_token_context(self, symbol: str):
        return {
            'symbol': symbol,
            'display_name': symbol,
            'price': 0.0,
            'liquidity': 0.0,
            'holders': 0,
            'top_holder_concentration_pct': 0.0,
            'market_rank_context': 'Visible on the board.',
            'signal_status': 'unmatched',
            'signal_trigger_context': '',
            'audit_flags': [],
            'major_risks': [],
            'smart_money_count': 0,
            'exit_rate': 0.0,
            'signal_age_hours': 0.0,
            'signal_freshness': 'UNKNOWN',
            'audit_gate': 'ALLOW',
            'blocked_reason': '',
        }


def test_analyze_token_propagates_quote_context_into_deep_brief():
    old_service = token_analysis.get_market_data_service
    old_fetch = token_analysis._fetch_market_quote
    token_analysis.get_market_data_service = lambda: DummyService()
    token_analysis._fetch_market_quote = lambda symbol: ({
        'price': 667.55,
        'percent_change_24h': 2.42,
        'rank': 4,
        'exchange_symbol': 'BNBUSDT',
        'spread_pct': 0.04,
        'volume_24h': 59300000,
    }, 'Binance Spot')
    try:
        brief = token_analysis.analyze_token('BNB')
    finally:
        token_analysis.get_market_data_service = old_service
        token_analysis._fetch_market_quote = old_fetch

    rendered = format_brief(brief)
    assert '**🧩 BNB $667.55 +2.42% 📈 #4**' in rendered
    assert 'Liquidity:' in rendered
    assert 'BNBUSDT' in rendered or '$59.3M' in rendered



def test_deep_brief_uses_market_active_setup_absent_when_price_exists_but_signal_does_not():
    old_service = token_analysis.get_market_data_service
    old_fetch = token_analysis._fetch_market_quote
    token_analysis.get_market_data_service = lambda: DummyService()
    token_analysis._fetch_market_quote = lambda symbol: ({
        'price': 667.55,
        'percent_change_24h': 2.42,
        'rank': 4,
        'exchange_symbol': 'BNBUSDT',
        'spread_pct': 0.04,
        'volume_24h': 59300000,
    }, 'Binance Spot')
    try:
        brief = token_analysis.analyze_token('BNB')
    finally:
        token_analysis.get_market_data_service = old_service
        token_analysis._fetch_market_quote = old_fetch

    rendered = format_brief(brief)
    assert 'Signal: No signal match' in rendered or 'Signal: Market active · setup absent' in rendered
    assert 'Holders: —' in rendered
    assert 'Smart money: none visible' in rendered
