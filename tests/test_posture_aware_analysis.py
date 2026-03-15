import src.analyzers.market_watch as market_watch


class DummyWatchService:
    def get_watch_today_context(self):
        return {
            'top_narratives': ['AI'],
            'strongest_signals': ['BNB strength'],
            'market_takeaway': 'Opportunity exists, but selectivity matters.',
        }


def test_watchtoday_adds_portfolio_posture_note():
    old_service = market_watch.get_market_data_service
    old_fetch = market_watch._fetch_market_quote
    old_loader = market_watch.load_portfolio_posture
    market_watch.get_market_data_service = lambda: DummyWatchService()
    market_watch._fetch_market_quote = lambda symbol: ({'percent_change_24h': 1.0, 'spread_pct': 0.02, 'exchange_symbol': f'{symbol}USDT'}, 'Binance Spot')
    market_watch.load_portfolio_posture = lambda: {'stable_pct': 65.0, 'concentration': 20.0}
    try:
        brief = market_watch.watch_today()
    finally:
        market_watch.get_market_data_service = old_service
        market_watch._fetch_market_quote = old_fetch
        market_watch.load_portfolio_posture = old_loader

    assert brief.entity == "Market Watch"
    assert brief.quick_verdict
