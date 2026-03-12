import src.analyzers.market_watch as market_watch
import src.analyzers.risk_analysis as risk_analysis


class DummyWatchService:
    def get_watch_today_context(self):
        return {
            'top_narratives': ['AI'],
            'strongest_signals': ['BNB strength'],
            'market_takeaway': 'Opportunity exists, but selectivity matters.',
        }


class DummyRiskService:
    def get_token_context(self, symbol: str):
        return {
            'symbol': symbol,
            'display_name': symbol,
            'liquidity': 1000000.0,
            'audit_flags': [],
            'major_risks': ['Base risk.'],
            'signal_status': 'watch',
        }

    def get_signal_context(self, symbol: str):
        return {
            'token': symbol,
            'signal_status': 'watch',
            'major_risks': [],
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

    assert 'stablecoin dry powder' in brief.quick_verdict.lower()


def test_risk_adds_portfolio_note():
    old_service = risk_analysis.get_market_data_service
    old_loader = risk_analysis.load_portfolio_posture
    old_cmc = risk_analysis._fetch_cmc_quote
    risk_analysis.get_market_data_service = lambda: DummyRiskService()
    risk_analysis.load_portfolio_posture = lambda: {'stable_pct': 70.0, 'concentration': 10.0, 'posture': 'defensive'}
    risk_analysis._fetch_cmc_quote = lambda symbol: None
    try:
        brief = risk_analysis.analyze_risk('BNB')
    finally:
        risk_analysis.get_market_data_service = old_service
        risk_analysis.load_portfolio_posture = old_loader
        risk_analysis._fetch_cmc_quote = old_cmc

    assert 'Current posture is fairly defensive' in brief.quick_verdict
