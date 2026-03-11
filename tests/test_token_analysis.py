import src.analyzers.token_analysis as token_analysis


class DummyService:
    def get_token_context(self, symbol: str):
        return {
            'symbol': symbol,
            'display_name': symbol,
            'liquidity': 1250000.0,
            'holders': 1000,
            'market_rank_context': 'large-cap with strong ecosystem relevance',
            'signal_status': 'watch',
            'signal_trigger_context': 'Momentum is improving but still needs confirmation.',
            'audit_flags': [],
            'major_risks': [],
        }


def test_analyze_token_adds_binance_spot_tag():
    old_service = token_analysis.get_market_data_service
    old_fetch = token_analysis._fetch_market_quote
    token_analysis.get_market_data_service = lambda: DummyService()
    token_analysis._fetch_market_quote = lambda symbol: ({
        'exchange_symbol': 'BNBUSDT',
        'spread_pct': 0.04,
        'percent_change_24h': 2.25,
    }, 'Binance Spot')
    try:
        brief = token_analysis.analyze_token('BNB')
    finally:
        token_analysis.get_market_data_service = old_service
        token_analysis._fetch_market_quote = old_fetch

    assert any(tag.name == 'Binance Spot' for tag in brief.risk_tags)
    assert 'Binance Spot confirms active pricing' in brief.why_it_matters
