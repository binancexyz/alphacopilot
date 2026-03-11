import src.analyzers.signal_check as signal_check


class DummyService:
    def get_signal_context(self, symbol: str):
        return {
            'token': symbol,
            'signal_status': 'unmatched',
            'major_risks': [],
            'audit_flags': [],
        }


def test_analyze_signal_adds_binance_spot_unmatched_note():
    old_service = signal_check.get_market_data_service
    old_fetch = signal_check._fetch_market_quote
    signal_check.get_market_data_service = lambda: DummyService()
    signal_check._fetch_market_quote = lambda symbol: ({
        'exchange_symbol': 'DOGEUSDT',
        'spread_pct': 0.03,
        'percent_change_24h': 4.2,
    }, 'Binance Spot')
    try:
        brief = signal_check.analyze_signal('DOGE')
    finally:
        signal_check.get_market_data_service = old_service
        signal_check._fetch_market_quote = old_fetch

    assert any(tag.name == 'Binance Spot' for tag in brief.risk_tags)
    assert 'signal itself is still unmatched' in brief.top_risks[0]
