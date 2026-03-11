from src.services.live_extractors import extract_wallet_context


def test_extract_wallet_context_builds_style_profile_and_exposures():
    raw = {
        'query-address-info': {
            'list': [
                {'symbol': 'BNB', 'price': 600, 'remainQty': 100, 'percentChange24h': 4.0},
                {'symbol': 'BTC', 'price': 70000, 'remainQty': 0.5, 'percentChange24h': 2.0},
                {'symbol': 'FET', 'price': 2.0, 'remainQty': 5000, 'percentChange24h': 12.0},
                {'symbol': 'LINK', 'price': 18, 'remainQty': 1000, 'percentChange24h': 6.0},
                {'symbol': 'DOGE', 'price': 0.18, 'remainQty': 50000, 'percentChange24h': 9.0},
            ]
        }
    }
    out = extract_wallet_context(raw, '0xabc')
    assert out['style_profile']
    assert out['exposure_breakdown']
    assert 'L1' in out['notable_exposures']
