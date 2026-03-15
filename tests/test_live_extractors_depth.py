from src.services.live_extractors import extract_meme_context, extract_watch_today_context


def test_extract_meme_context_enriches_participation_fields():
    raw = {
        'query-token-info': {
            'metadata': {'symbol': 'DOGE', 'name': 'Dogecoin'},
            'dynamic': {
                'smartMoneyHolders': '9',
                'kolHolders': '4',
                'kolHoldingPercent': '6.5',
                'proHolders': '2',
                'proHoldingPercent': '3.2',
            },
        },
        'crypto-market-rank': {
            'data': {
                'tokens': [
                    {
                        'symbol': 'DOGE',
                        'holdersTop10Percent': 82,
                        'socialHypeInfo': {'socialSummaryBrief': 'Viral meme/community attention is accelerating.'},
                    }
                ]
            },
            'smart_money_inflow': [{'tokenName': 'DOGE', 'inflow': '125000'}],
        },
        'trading-signal': {'data': [{'ticker': 'DOGE', 'status': 'watch', 'smartMoneyCount': 3}]},
        'meme-rush': {'data': [{'symbol': 'DOGE', 'topicHeatScore': 77}]},
        'query-token-audit': {},
    }
    out = extract_meme_context(raw, 'DOGE')
    assert out['social_brief']
    assert out['meme_score'] == 77
    assert out['top_holder_concentration_pct'] == 82
    assert out['smart_money_holders'] == 9
    assert out['smart_money_inflow_usd'] == 125000.0
    assert out['kol_holders'] == 4
    assert out['kol_holding_pct'] == 6.5
    assert out['pro_holders'] == 2
    assert out['pro_holding_pct'] == 3.2


def test_extract_watch_today_context_adds_exchange_board():
    raw = {
        'crypto-market-rank': {
            'data': {
                'tokens': [
                    {'symbol': 'BNB', 'priceChangePercent24h': 2.4, 'liquidity': 1200000000},
                    {'symbol': 'BTC', 'priceChangePercent24h': 1.1, 'liquidity': 900000000},
                ]
            }
        },
        'trading-signal': {},
        'meme-rush': {},
    }
    out = extract_watch_today_context(raw)
    assert out['exchange_board']
    assert 'BNB +2.4%' in out['exchange_board'][0]
