import src.analyzers.brief_analysis as brief_analysis
from src.models.context import SignalContext, TokenContext


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


def test_analyze_brief_uses_binance_spot_context():
    old_service = brief_analysis.get_market_data_service
    old_fetch = brief_analysis._fetch_market_quote
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
    try:
        brief = brief_analysis.analyze_brief('BNB')
    finally:
        brief_analysis.get_market_data_service = old_service
        brief_analysis._fetch_market_quote = old_fetch

    assert brief.entity == 'Brief: BNB'
    assert 'BNBUSDT' in brief.quick_verdict
    assert 'Worth watching; exchange price context looks clean enough' in brief.quick_verdict


def test_analyze_brief_handles_unmatched_signal_with_binance_spot():
    class UnmatchedService(DummyService):
        def get_signal_context(self, symbol: str):
            return {
                'token': symbol,
                'signal_status': 'unmatched',
                'major_risks': [],
            }

    old_service = brief_analysis.get_market_data_service
    old_fetch = brief_analysis._fetch_market_quote
    brief_analysis.get_market_data_service = lambda: UnmatchedService()
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
    try:
        brief = brief_analysis.analyze_brief('BNB')
    finally:
        brief_analysis.get_market_data_service = old_service
        brief_analysis._fetch_market_quote = old_fetch

    assert 'no matched live smart-money signal' in brief.quick_verdict
