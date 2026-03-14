import src.analyzers.brief_analysis as brief_analysis


class DummyService:
    def get_token_context(self, symbol: str):
        return {
            'symbol': symbol,
            'display_name': symbol,
            'price': 0.0,
            'liquidity': 1250000.0,
            'holders': 1000,
            'signal_status': 'watch',
            'kline_trend': 'rising',
            'major_risks': [],
            'audit_flags': [],
        }

    def get_signal_context(self, symbol: str):
        return {
            'token': symbol,
            'signal_status': 'watch',
            'major_risks': [],
        }


def test_analyze_brief_uses_binance_spot_context():
    old_service = brief_analysis.get_market_data_service
    old_fetch = brief_analysis._fetch_market_quote
    brief_analysis.get_market_data_service = lambda: DummyService()
    brief_analysis._fetch_market_quote = lambda symbol: ({
        'name': 'BNB',
        'symbol': 'BNB',
        'price': 612.5,
        'percent_change_24h': 3.25,
        'rank': 0,
        'spread_pct': 0.04,
        'exchange_symbol': 'BNBUSDT',
        'source': 'Binance Spot',
    }, 'Binance Spot')
    try:
        brief = brief_analysis.analyze_brief('BNB')
    finally:
        brief_analysis.get_market_data_service = old_service
        brief_analysis._fetch_market_quote = old_fetch

    assert brief.entity == 'Brief: BNB'
    assert 'BNBUSDT' in brief.quick_verdict
    assert 'Clean price context' in brief.quick_verdict


def test_analyze_brief_handles_unmatched_signal_with_binance_spot():
    class UnmatchedService(DummyService):
        def get_signal_context(self, symbol: str):
            return {
                'token': symbol,
                'signal_status': 'unmatched',
                'major_risks': [],
            }

    old_service = brief_analysis.get_market_data_service
    old_fetch = brief_analysis._fetch_market_quote
    brief_analysis.get_market_data_service = lambda: UnmatchedService()
    brief_analysis._fetch_market_quote = lambda symbol: ({
        'name': 'BNB',
        'symbol': 'BNB',
        'price': 612.5,
        'percent_change_24h': 3.25,
        'rank': 0,
        'spread_pct': 0.04,
        'exchange_symbol': 'BNBUSDT',
        'source': 'Binance Spot',
    }, 'Binance Spot')
    try:
        brief = brief_analysis.analyze_brief('BNB')
    finally:
        brief_analysis.get_market_data_service = old_service
        brief_analysis._fetch_market_quote = old_fetch

    assert 'no matched live smart-money signal' in brief.quick_verdict


def test_analyze_brief_adds_bid_heavy_order_book_tag():
    old_service = brief_analysis.get_market_data_service
    old_fetch = brief_analysis._fetch_market_quote
    brief_analysis.get_market_data_service = lambda: DummyService()
    brief_analysis._fetch_market_quote = lambda symbol: ({
        'name': 'BNB',
        'symbol': 'BNB',
        'price': 612.5,
        'percent_change_24h': 3.25,
        'rank': 0,
        'spread_pct': 0.04,
        'exchange_symbol': 'BNBUSDT',
        'source': 'Binance Spot',
        'bid_qty': 1000.0,
        'ask_qty': 300.0,
    }, 'Binance Spot')
    try:
        brief = brief_analysis.analyze_brief('BNB')
    finally:
        brief_analysis.get_market_data_service = old_service
        brief_analysis._fetch_market_quote = old_fetch

    assert any(tag.name == 'Order Book' and 'Bid depth significantly outweighs ask depth' in str(tag.note) for tag in brief.risk_tags)


def test_analyze_brief_adds_ask_heavy_order_book_tag():
    old_service = brief_analysis.get_market_data_service
    old_fetch = brief_analysis._fetch_market_quote
    brief_analysis.get_market_data_service = lambda: DummyService()
    brief_analysis._fetch_market_quote = lambda symbol: ({
        'name': 'BNB',
        'symbol': 'BNB',
        'price': 612.5,
        'percent_change_24h': 3.25,
        'rank': 0,
        'spread_pct': 0.04,
        'exchange_symbol': 'BNBUSDT',
        'source': 'Binance Spot',
        'bid_qty': 300.0,
        'ask_qty': 1000.0,
    }, 'Binance Spot')
    try:
        brief = brief_analysis.analyze_brief('BNB')
    finally:
        brief_analysis.get_market_data_service = old_service
        brief_analysis._fetch_market_quote = old_fetch

    assert any(tag.name == 'Order Book' and 'Ask depth significantly outweighs bid depth' in str(tag.note) for tag in brief.risk_tags)


def test_analyze_brief_adds_fresh_market_maturity_tag():
    old_service = brief_analysis.get_market_data_service
    old_fetch = brief_analysis._fetch_market_quote
    brief_analysis.get_market_data_service = lambda: DummyService()
    brief_analysis._fetch_market_quote = lambda symbol: ({
        'name': 'BNB',
        'symbol': 'BNB',
        'price': 612.5,
        'percent_change_24h': 3.25,
        'rank': 0,
        'spread_pct': 0.04,
        'exchange_symbol': 'BNBUSDT',
        'source': 'Binance Spot',
        'trading_days': 10,
    }, 'Binance Spot')
    
    try:
        brief = brief_analysis.analyze_brief('BNB')
    finally:
        brief_analysis.get_market_data_service = old_service
        brief_analysis._fetch_market_quote = old_fetch

    assert any(tag.name == 'Maturity' and 'Very fresh market' in str(tag.note) for tag in brief.risk_tags)


def test_analyze_brief_adds_vintage_market_maturity_tag():
    old_service = brief_analysis.get_market_data_service
    old_fetch = brief_analysis._fetch_market_quote
    brief_analysis.get_market_data_service = lambda: DummyService()
    brief_analysis._fetch_market_quote = lambda symbol: ({
        'name': 'BNB',
        'symbol': 'BNB',
        'price': 612.5,
        'percent_change_24h': 3.25,
        'rank': 0,
        'spread_pct': 0.04,
        'exchange_symbol': 'BNBUSDT',
        'source': 'Binance Spot',
        'trading_days': 400,
    }, 'Binance Spot')
    
    try:
        brief = brief_analysis.analyze_brief('BNB')
    finally:
        brief_analysis.get_market_data_service = old_service
        brief_analysis._fetch_market_quote = old_fetch

    assert any(tag.name == 'Maturity' and 'Vintage market' in str(tag.note) for tag in brief.risk_tags)


def test_analyze_brief_packs_market_fields_and_boosts_active_smart_money_quality():
    class ActiveService(DummyService):
        def get_signal_context(self, symbol: str):
            return {
                'token': symbol,
                'signal_status': 'active',
                'smart_money_count': 4,
                'major_risks': [],
            }

    old_service = brief_analysis.get_market_data_service
    old_fetch = brief_analysis._fetch_market_quote
    brief_analysis.get_market_data_service = lambda: ActiveService()
    brief_analysis._fetch_market_quote = lambda symbol: ({
        'name': 'BNB',
        'symbol': 'BNB',
        'price': 612.5,
        'percent_change_24h': 3.25,
        'rank': 0,
        'spread_pct': 0.04,
        'exchange_symbol': 'BNBUSDT',
        'source': 'Binance Spot',
        'volume_24h': 1_200_000_000,
        'market_cap': 85_000_000_000,
    }, 'Binance Spot')
    try:
        brief = brief_analysis.analyze_brief('BNB')
    finally:
        brief_analysis.get_market_data_service = old_service
        brief_analysis._fetch_market_quote = old_fetch

    fields = brief.quick_verdict.split("|")
    assert brief.signal_quality == "High"
    assert fields[9] == "1200000000.0"
    assert fields[10] == "85000000000.0"
    assert fields[11] == "4"
    assert fields[12] == "rising"
