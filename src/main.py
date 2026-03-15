from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.analyzers.alpha_analysis import analyze_alpha
from src.analyzers.audit_analysis import analyze_audit
from src.analyzers.brief_analysis import analyze_brief
from src.analyzers.futures_analysis import analyze_futures
from src.analyzers.market_watch import watch_today
from src.analyzers.portfolio_analysis import analyze_portfolio
from src.analyzers.signal_check import analyze_signal
from src.analyzers.token_analysis import analyze_token
from src.analyzers.wallet_analysis import analyze_wallet
from src.formatters.brief_formatter import format_brief
from src.services.factory import get_market_data_service
from src.utils.parsing import normalize_token_input, normalize_wallet_input


def _analyze_alpha(symbol: str | None):
    normalized = normalize_token_input(symbol) if symbol else ""
    return analyze_alpha(normalized or None, get_market_data_service().get_alpha_context(normalized))


def _analyze_futures(symbol: str):
    normalized = normalize_token_input(symbol)
    return analyze_futures(normalized, get_market_data_service().get_futures_context(normalized))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bibipilot CLI",
        epilog=(
            "Canonical commands: brief <symbol>, signal <symbol>, audit <symbol>, "
            "portfolio, wallet <address>, watchtoday, alpha [symbol], futures <symbol>"
        ),
    )
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        metavar="{brief,signal,audit,portfolio,wallet,watchtoday,alpha,futures,holdings}",
    )

    brief_parser = subparsers.add_parser("brief", help="fast default read; add 'deep' for fuller token judgment")
    brief_parser.add_argument("symbol")
    brief_parser.add_argument("mode", nargs="?", choices=["deep"], help=argparse.SUPPRESS)

    signal_parser = subparsers.add_parser("signal", help="setup, risk, and invalidation")
    signal_parser.add_argument("token")

    subparsers.add_parser("watchtoday", help="daily market board")

    audit_parser = subparsers.add_parser("audit", help="safety read with merged meme lens")
    audit_parser.add_argument("symbol")

    subparsers.add_parser("portfolio", help="Binance Spot portfolio posture")

    wallet_parser = subparsers.add_parser("wallet", help="external wallet behavior and concentration read")
    wallet_parser.add_argument("address")

    alpha_parser = subparsers.add_parser("alpha", help="Binance Alpha board or symbol-specific Alpha context")
    alpha_parser.add_argument("symbol", nargs="?")

    futures_parser = subparsers.add_parser("futures", help="Binance Futures positioning and squeeze context")
    futures_parser.add_argument("symbol")

    holdings_parser = subparsers.add_parser("holdings", help="legacy alias for portfolio or wallet")
    holdings_parser.add_argument("target", nargs="?", help="optional wallet address; omit for your Binance Spot posture")

    args = parser.parse_args()

    if args.command == "brief":
        symbol = normalize_token_input(args.symbol)
        brief = analyze_token(symbol) if getattr(args, "mode", None) == "deep" else analyze_brief(symbol)
    elif args.command == "audit":
        brief = analyze_audit(normalize_token_input(args.symbol))
    elif args.command == "portfolio":
        brief = analyze_portfolio()
    elif args.command == "wallet":
        brief = analyze_wallet(normalize_wallet_input(args.address))
    elif args.command == "alpha":
        brief = _analyze_alpha(getattr(args, "symbol", None))
    elif args.command == "futures":
        brief = _analyze_futures(args.symbol)
    elif args.command == "holdings":
        target = str(getattr(args, "target", "") or "").strip()
        brief = analyze_wallet(normalize_wallet_input(target)) if target.startswith("0x") else analyze_portfolio()
    elif args.command == "signal":
        brief = analyze_signal(normalize_token_input(args.token))
    else:
        brief = watch_today()

    print(format_brief(brief))


if __name__ == "__main__":
    main()
