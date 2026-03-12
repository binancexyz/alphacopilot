import src.services.exposure_groups as exposure_groups


def test_top_groups_ranks_exposure_buckets():
    groups = exposure_groups.top_groups([
        {'asset': 'USDT', 'usd_value': 500},
        {'asset': 'USDC', 'usd_value': 300},
        {'asset': 'BNB', 'usd_value': 100},
        {'asset': 'PENGU', 'usd_value': 100},
    ])
    assert groups[0][0] == 'Stablecoins'
    assert groups[0][1] > groups[1][1]


def test_classify_asset_supports_exchange_and_data_buckets():
    assert exposure_groups.classify_asset('BNB') == 'Exchange'
    assert exposure_groups.classify_asset('SXT') == 'AI'
    assert exposure_groups.classify_asset('WAL') == 'Data'
