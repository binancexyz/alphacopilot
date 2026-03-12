import src.analyzers.brief_analysis as brief_analysis


class DummyService:
    def get_token_context(self, symbol: str):
        return {
            'symbol': symbol,
            'display_name': symbol,
            'price': 0.0,
            'liquidity': 1250000.0,
            'holders': 1000,
            'signal_status': 'watch',
            'major_risks': [],
            'audit_flags': [],
        }

    def get_signal_context(self, symbol: str):
        return {
            'token': symbol,
            'signal_status': 'watch',
            'major_risks': [],
        }


def test_analyze_brief_adds_portfolio_posture_note():
    old_service = brief_analysis.get_market_data_service
    old_fetch = brief_analysis._fetch_market_quote
    old_loader = brief_analysis.load_portfolio_posture
    brief_analysis.get_market_data_service = lambda: DummyService()
    brief_analysis._fetch_market_quote = lambda symbol: ({
        'name': 'BNB',
        'symbol': 'BNB',
        'price': 612.5,
        'percent_change_24h': 3.25,
        'rank': 0,
        'spread_pct': 0.04,
        'exchange_symbol': 'BNBUSDT',
        'source': 'Binance Spot',
    }, 'Binance Spot')
    brief_analysis.load_portfolio_posture = lambda: {'stable_pct': 70.0, 'concentration': 10.0, 'posture': 'defensive'}
    try:
        brief = brief_analysis.analyze_brief('BNB')
    finally:
        brief_analysis.get_market_data_service = old_service
        brief_analysis._fetch_market_quote = old_fetch
        brief_analysis.load_portfolio_posture = old_loader

    assert 'Current posture is fairly defensive' in brief.quick_verdict
