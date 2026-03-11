import src.analyzers.market_watch as market_watch


class DummyService:
    def get_watch_today_context(self):
        return {
            'top_narratives': ['AI'],
            'strongest_signals': ['BNB strength'],
            'market_takeaway': 'Opportunity exists, but selectivity matters.',
        }


def test_watch_today_adds_exchange_board_from_binance_spot():
    old_service = market_watch.get_market_data_service
    old_fetch = market_watch._fetch_market_quote
    market_watch.get_market_data_service = lambda: DummyService()

    prices = {
        'BNB': ({'percent_change_24h': 2.4, 'spread_pct': 0.04, 'exchange_symbol': 'BNBUSDT'}, 'Binance Spot'),
        'BTC': ({'percent_change_24h': 1.1, 'spread_pct': 0.02, 'exchange_symbol': 'BTCUSDT'}, 'Binance Spot'),
        'SOL': ({'percent_change_24h': -0.6, 'spread_pct': 0.08, 'exchange_symbol': 'SOLUSDT'}, 'Binance Spot'),
    }
    market_watch._fetch_market_quote = lambda symbol: prices[symbol]
    try:
        brief = market_watch.watch_today()
    finally:
        market_watch.get_market_data_service = old_service
        market_watch._fetch_market_quote = old_fetch

    titles = [section.title for section in brief.sections]
    assert '🏦 Exchange Board' in titles
    section = next(section for section in brief.sections if section.title == '🏦 Exchange Board')
    assert 'BNB +2.40% | BNBUSDT | strong' in section.content
