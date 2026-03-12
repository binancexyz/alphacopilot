from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.analyzers.audit_analysis import analyze_audit
from src.analyzers.brief_analysis import analyze_brief
from src.analyzers.market_watch import watch_today
from src.analyzers.portfolio_analysis import analyze_portfolio
from src.analyzers.signal_check import analyze_signal
from src.analyzers.token_analysis import analyze_token
from src.analyzers.wallet_analysis import analyze_wallet
from src.formatters.brief_formatter import format_brief
from src.utils.parsing import normalize_token_input, normalize_wallet_input


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bibipilot CLI",
        epilog="Canonical commands: brief <symbol>, signal <symbol>, holdings [address], watchtoday, audit <symbol>",
    )
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        metavar="{brief,signal,holdings,watchtoday,audit}",
    )

    brief_parser = subparsers.add_parser("brief", help="fast default read; add 'deep' for fuller token judgment")
    brief_parser.add_argument("symbol")
    brief_parser.add_argument("mode", nargs="?", choices=["deep"], help=argparse.SUPPRESS)

    signal_parser = subparsers.add_parser("signal", help="setup, risk, and invalidation")
    signal_parser.add_argument("token")

    holdings_parser = subparsers.add_parser("holdings", help="portfolio posture or external wallet behavior")
    holdings_parser.add_argument("target", nargs="?", help="optional wallet address; omit for your Binance Spot posture")

    subparsers.add_parser("watchtoday", help="daily market board")

    audit_parser = subparsers.add_parser("audit", help="safety read with merged meme lens")
    audit_parser.add_argument("symbol")

    args = parser.parse_args()

    if args.command == "brief":
        symbol = normalize_token_input(args.symbol)
        brief = analyze_token(symbol) if getattr(args, "mode", None) == "deep" else analyze_brief(symbol)
    elif args.command == "audit":
        brief = analyze_audit(normalize_token_input(args.symbol))
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
