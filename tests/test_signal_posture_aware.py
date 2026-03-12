import src.analyzers.signal_check as signal_check


class DummyService:
    def get_signal_context(self, symbol: str):
        return {
            'token': symbol,
            'signal_status': 'watch',
            'major_risks': [],
            'audit_flags': [],
        }


def test_signal_adds_portfolio_posture_note():
    old_service = signal_check.get_market_data_service
    old_fetch = signal_check._fetch_market_quote
    old_append = signal_check.append_posture_note_to_brief
    signal_check.get_market_data_service = lambda: DummyService()
    signal_check._fetch_market_quote = lambda symbol: ({
        'exchange_symbol': 'DOGEUSDT',
        'spread_pct': 0.03,
        'percent_change_24h': 4.2,
    }, 'Binance Spot')
    signal_check.append_posture_note_to_brief = lambda brief, symbol: (brief.top_risks.append('Current posture is fairly defensive, so higher-beta ideas should earn their place instead of being chased by default.'), brief.__setattr__('why_it_matters', f"{brief.why_it_matters} Current posture is fairly defensive, so higher-beta ideas should earn their place instead of being chased by default.".strip()))
    try:
        brief = signal_check.analyze_signal('DOGE')
    finally:
        signal_check.get_market_data_service = old_service
        signal_check._fetch_market_quote = old_fetch
        signal_check.append_posture_note_to_brief = old_append

    joined = ' '.join(brief.top_risks + [brief.why_it_matters])
    assert 'Current posture is fairly defensive' in joined
