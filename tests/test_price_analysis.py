import src.analyzers.price_analysis as price_analysis


class _DummyResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class _DummyClient:
    def __init__(self, responses):
        self.responses = responses

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def get(self, url, params=None, headers=None):
        if url.endswith('/api/v3/exchangeInfo'):
            return _DummyResponse({
                'symbols': [
                    {'symbol': 'BNBUSDT', 'status': 'TRADING'},
                ]
            })
        if url.endswith('/api/v3/ticker/24hr'):
            return _DummyResponse({
                'lastPrice': '612.50',
                'priceChangePercent': '3.25',
                'highPrice': '620.00',
                'lowPrice': '590.00',
                'quoteVolume': '123456789.00',
                'weightedAvgPrice': '605.00',
            })
        if url.endswith('/api/v3/ticker/bookTicker'):
            return _DummyResponse({
                'bidPrice': '612.40',
                'askPrice': '612.60',
            })
        if url.endswith('/api/v3/avgPrice'):
            return _DummyResponse({'price': '606.00'})
        raise AssertionError(f'unexpected url {url}')


def test_fetch_binance_spot_quote_prefers_usdt_pair():
    old_client = price_analysis.httpx.Client
    price_analysis.httpx.Client = lambda *args, **kwargs: _DummyClient({})
    try:
        quote = price_analysis._fetch_binance_spot_quote('BNB')
    finally:
        price_analysis.httpx.Client = old_client

    assert quote is not None
    assert quote['source'] == 'Binance Spot'
    assert quote['exchange_symbol'] == 'BNBUSDT'
    assert quote['price'] == 612.5
    assert quote['symbol'] == 'BNB'


def test_analyze_price_uses_binance_spot_when_available():
    old_fetch = price_analysis._fetch_market_quote
    price_analysis._fetch_market_quote = lambda symbol: ({
        'name': 'BNB',
        'symbol': 'BNB',
        'link': 'https://www.binance.com/en/trade/BNB_USDT',
        'rank': 0,
        'price': 612.5,
        'percent_change_24h': 3.25,
        'high_24h': 620.0,
        'low_24h': 590.0,
        'market_cap': 0.0,
        'volume_24h': 123456789.0,
        'spread_pct': 0.03,
        'exchange_symbol': 'BNBUSDT',
        'source': 'Binance Spot',
    }, 'Binance Spot')
    try:
        brief = price_analysis.analyze_price('BNB')
    finally:
        price_analysis._fetch_market_quote = old_fetch

    assert brief.entity == 'Price: BNB'
    assert brief.signal_quality == 'High'
    assert 'Binance Spot market data' in brief.top_risks[0]
