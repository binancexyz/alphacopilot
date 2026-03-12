import src.analyzers.token_analysis as token_analysis


class DummyService:
    def get_token_context(self, symbol: str):
        return {
            'symbol': symbol,
            'display_name': symbol,
            'price': 10.0,
            'liquidity': 1000000.0,
            'holders': 100,
            'market_rank_context': 'Visible on the board.',
            'signal_status': 'watch',
            'signal_trigger_context': 'Signal context exists.',
            'audit_flags': [],
            'major_risks': ['Base token risk.'],
            'smart_money_count': 0,
            'exit_rate': 0.0,
            'signal_age_hours': 0.0,
            'signal_freshness': 'UNKNOWN',
            'audit_gate': 'ALLOW',
            'blocked_reason': '',
        }


def test_token_adds_portfolio_posture_note():
    old_service = token_analysis.get_market_data_service
    old_fetch = token_analysis._fetch_market_quote
    old_append = token_analysis.append_posture_note_to_brief
    token_analysis.get_market_data_service = lambda: DummyService()
    token_analysis._fetch_market_quote = lambda symbol: ({'exchange_symbol': f'{symbol}USDT', 'spread_pct': 0.1, 'percent_change_24h': 2.0}, 'Binance Spot')
    token_analysis.append_posture_note_to_brief = lambda brief, symbol: brief.top_risks.append('Current posture is fairly defensive, so higher-beta ideas should earn their place instead of being chased by default.')
    try:
        brief = token_analysis.analyze_token('BNB')
    finally:
        token_analysis.get_market_data_service = old_service
        token_analysis._fetch_market_quote = old_fetch
        token_analysis.append_posture_note_to_brief = old_append

    joined = ' '.join(brief.top_risks + [brief.why_it_matters])
    assert 'Current posture is fairly defensive' in joined
