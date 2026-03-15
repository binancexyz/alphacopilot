import io
import sys
from contextlib import redirect_stdout

import src.main as main_module


class DummyService:
    def get_alpha_context(self, symbol: str):
        return {"kind": "alpha", "symbol": symbol}

    def get_futures_context(self, symbol: str):
        return {"kind": "futures", "symbol": symbol}


def _run_cli(argv: list[str]) -> str:
    old_argv = sys.argv[:]
    sys.argv = argv
    try:
        buf = io.StringIO()
        with redirect_stdout(buf):
            main_module.main()
        return buf.getvalue().strip()
    finally:
        sys.argv = old_argv


def test_main_routes_portfolio_command():
    old_analyze_portfolio = main_module.analyze_portfolio
    old_format_brief = main_module.format_brief
    try:
        main_module.analyze_portfolio = lambda: "portfolio-brief"
        main_module.format_brief = lambda brief: str(brief)
        out = _run_cli(["main.py", "portfolio"])
        assert out == "portfolio-brief"
    finally:
        main_module.analyze_portfolio = old_analyze_portfolio
        main_module.format_brief = old_format_brief


def test_main_routes_wallet_command():
    old_analyze_wallet = main_module.analyze_wallet
    old_format_brief = main_module.format_brief
    try:
        main_module.analyze_wallet = lambda address: f"wallet:{address}"
        main_module.format_brief = lambda brief: str(brief)
        out = _run_cli(["main.py", "wallet", "0x1234567890ab"])
        assert out == "wallet:0x1234567890ab"
    finally:
        main_module.analyze_wallet = old_analyze_wallet
        main_module.format_brief = old_format_brief


def test_main_routes_alpha_command_without_symbol():
    old_get_market_data_service = main_module.get_market_data_service
    old_analyze_alpha = main_module.analyze_alpha
    old_format_brief = main_module.format_brief
    try:
        main_module.get_market_data_service = lambda: DummyService()
        main_module.analyze_alpha = lambda symbol, ctx: f"alpha:{symbol}:{ctx['kind']}:{ctx['symbol']}"
        main_module.format_brief = lambda brief: str(brief)
        out = _run_cli(["main.py", "alpha"])
        assert out == "alpha:None:alpha:"
    finally:
        main_module.get_market_data_service = old_get_market_data_service
        main_module.analyze_alpha = old_analyze_alpha
        main_module.format_brief = old_format_brief


def test_main_routes_futures_command():
    old_get_market_data_service = main_module.get_market_data_service
    old_analyze_futures = main_module.analyze_futures
    old_format_brief = main_module.format_brief
    try:
        main_module.get_market_data_service = lambda: DummyService()
        main_module.analyze_futures = lambda symbol, ctx: f"futures:{symbol}:{ctx['kind']}:{ctx['symbol']}"
        main_module.format_brief = lambda brief: str(brief)
        out = _run_cli(["main.py", "futures", "btc"])
        assert out == "futures:BTC:futures:BTC"
    finally:
        main_module.get_market_data_service = old_get_market_data_service
        main_module.analyze_futures = old_analyze_futures
        main_module.format_brief = old_format_brief


def test_main_routes_holdings_alias_to_wallet():
    old_analyze_portfolio = main_module.analyze_portfolio
    old_analyze_wallet = main_module.analyze_wallet
    old_format_brief = main_module.format_brief
    try:
        main_module.analyze_portfolio = lambda: "portfolio-brief"
        main_module.analyze_wallet = lambda address: f"wallet:{address}"
        main_module.format_brief = lambda brief: str(brief)
        out = _run_cli(["main.py", "holdings", "0x1234567890ab"])
        assert out == "wallet:0x1234567890ab"
    finally:
        main_module.analyze_portfolio = old_analyze_portfolio
        main_module.analyze_wallet = old_analyze_wallet
        main_module.format_brief = old_format_brief
