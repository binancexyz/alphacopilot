from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.analyzers.brief_analysis import analyze_brief
from src.analyzers.market_watch import watch_today
from src.analyzers.price_analysis import analyze_price
from src.analyzers.risk_analysis import analyze_risk
from src.analyzers.signal_check import analyze_signal
from src.analyzers.token_analysis import analyze_token
from src.analyzers.wallet_analysis import analyze_wallet
from src.formatters.brief_formatter import format_brief
from src.utils.parsing import normalize_token_input, normalize_wallet_input


def main() -> None:
    parser = argparse.ArgumentParser(description="Bibipilot scaffold CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    token_parser = subparsers.add_parser("token")
    token_parser.add_argument("symbol")

    brief_parser = subparsers.add_parser("brief")
    brief_parser.add_argument("symbol")

    price_parser = subparsers.add_parser("price")
    price_parser.add_argument("symbol")

    risk_parser = subparsers.add_parser("risk")
    risk_parser.add_argument("symbol")

    wallet_parser = subparsers.add_parser("wallet")
    wallet_parser.add_argument("address")

    signal_parser = subparsers.add_parser("signal")
    signal_parser.add_argument("token")

    watch_parser = subparsers.add_parser("watch")
    watch_parser.add_argument("scope", nargs="?", default="today")

    subparsers.add_parser("watchtoday")

    args = parser.parse_args()

    if args.command == "token":
        brief = analyze_token(normalize_token_input(args.symbol))
    elif args.command == "brief":
        brief = analyze_brief(normalize_token_input(args.symbol))
    elif args.command == "price":
        brief = analyze_price(normalize_token_input(args.symbol))
    elif args.command == "risk":
        brief = analyze_risk(normalize_token_input(args.symbol))
    elif args.command == "wallet":
        brief = analyze_wallet(normalize_wallet_input(args.address))
    elif args.command == "signal":
        brief = analyze_signal(normalize_token_input(args.token))
    elif args.command == "watch":
        scope = str(args.scope or "today").strip().lower().replace("-", "")
        if scope not in {"today", "todays"}:
            raise SystemExit("watch currently supports only: watch today")
        brief = watch_today()
    else:
        brief = watch_today()

    print(format_brief(brief))


if __name__ == "__main__":
    main()
