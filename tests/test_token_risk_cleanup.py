import src.analyzers.token_analysis as token_analysis


class DummyService:
    def get_token_context(self, symbol: str):
        return {
            'symbol': symbol,
            'display_name': symbol,
            'price': 0.0,
            'liquidity': 0.0,
            'holders': 1,
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


def test_analyze_token_removes_stale_low_liquidity_risk_when_quote_backfill_is_strong():
    old_service = token_analysis.get_market_data_service
    old_fetch = token_analysis._fetch_market_quote
    token_analysis.get_market_data_service = lambda: DummyService()
    token_analysis._fetch_market_quote = lambda symbol: ({
        'price': 72495.0,
        'percent_change_24h': 2.99,
        'rank': 1,
        'exchange_symbol': 'BTCUSDT',
        'spread_pct': 0.01,
        'volume_24h': 50200000000,
    }, 'Binance Spot')
    try:
        brief = token_analysis.analyze_token('BTC')
    finally:
        token_analysis.get_market_data_service = old_service
        token_analysis._fetch_market_quote = old_fetch

    joined = ' '.join(brief.top_risks)
    assert 'Low liquidity' not in joined
    assert 'liquidity is very thin' not in joined.lower()
    assert 'liquidity context is missing or weak' not in joined.lower()
