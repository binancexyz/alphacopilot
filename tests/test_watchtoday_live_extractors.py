from src.services.live_extractors import extract_watch_today_context


def test_extract_watchtoday_context_backfills_sparse_lanes_from_exchange_board_and_narratives():
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
        'meme-rush': {'top_narratives': ['meme rotation', 'AI']},
    }
    out = extract_watch_today_context(raw)
    assert out['exchange_board']
    assert out['trending_now']
    assert out['strongest_signals']
    assert out['social_hype']
    assert out['top_picks']
