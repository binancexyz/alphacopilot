import src.analyzers.wallet_analysis as wallet_analysis


class DummyService:
    def get_wallet_context(self, address: str):
        return {
            'address': address,
            'portfolio_value': 240000.0,
            'holdings_count': 7,
            'top_holdings': [
                {'symbol': 'BNB', 'weight_pct': 38.5},
                {'symbol': 'BTC', 'weight_pct': 17.0},
            ],
            'top_concentration_pct': 38.5,
            'change_24h': 5.1,
            'notable_exposures': ['AI', 'L1'],
            'follow_verdict': 'Track',
            'style_read': 'Narrative bias: AI, L1 | Style profile: selective diversified momentum-seeking | Risk posture: diversified',
            'style_profile': 'selective diversified momentum-seeking',
            'exposure_breakdown': ['L1 55.5%', 'AI 22.0%'],
        }


def test_analyze_wallet_adds_lead_holding_tag():
    old_service = wallet_analysis.get_market_data_service
    wallet_analysis.get_market_data_service = lambda: DummyService()
    try:
        brief = wallet_analysis.analyze_wallet('0xabc')
    finally:
        wallet_analysis.get_market_data_service = old_service

    assert any(tag.name == 'Lead Holding' for tag in brief.risk_tags)
    assert any(tag.name == 'Style Profile' for tag in brief.risk_tags)
    assert 'more useful for behavior study' in brief.why_it_matters
    assert 'Exposure mix:' in brief.why_it_matters
