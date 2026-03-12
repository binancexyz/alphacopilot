from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.analyzers.audit_analysis import analyze_audit
from src.analyzers.brief_analysis import analyze_brief
from src.analyzers.market_watch import watch_today
from src.analyzers.meme_analysis import analyze_meme
from src.analyzers.portfolio_analysis import analyze_portfolio
from src.analyzers.price_analysis import analyze_price
from src.analyzers.risk_analysis import analyze_risk
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

    token_parser = subparsers.add_parser("token", help=argparse.SUPPRESS)
    token_parser.add_argument("symbol")

    price_parser = subparsers.add_parser("price", help=argparse.SUPPRESS)
    price_parser.add_argument("symbol")

    risk_parser = subparsers.add_parser("risk", help=argparse.SUPPRESS)
    risk_parser.add_argument("symbol")

    meme_parser = subparsers.add_parser("meme", help=argparse.SUPPRESS)
    meme_parser.add_argument("symbol")

    wallet_parser = subparsers.add_parser("wallet", help=argparse.SUPPRESS)
    wallet_parser.add_argument("address")

    subparsers.add_parser("portfolio", help=argparse.SUPPRESS)

    watch_parser = subparsers.add_parser("watch", help=argparse.SUPPRESS)
    watch_parser.add_argument("scope", nargs="?", default="today")

    careers_parser = subparsers.add_parser("careers", help=argparse.SUPPRESS)
    careers_parser.add_argument("--limit", type=int, default=6)
    careers_parser.add_argument("--cache-only", action="store_true")

    hidden_commands = {"token", "price", "risk", "meme", "wallet", "portfolio", "watch", "careers"}
    subparsers._choices_actions = [
        action for action in subparsers._choices_actions if getattr(action, "dest", None) not in hidden_commands
    ]

    args = parser.parse_args()

    if args.command == "token":
        brief = analyze_token(normalize_token_input(args.symbol))
    elif args.command == "brief":
        symbol = normalize_token_input(args.symbol)
        brief = analyze_token(symbol) if getattr(args, "mode", None) == "deep" else analyze_brief(symbol)
    elif args.command == "price":
        brief = analyze_price(normalize_token_input(args.symbol))
    elif args.command == "risk":
        brief = analyze_risk(normalize_token_input(args.symbol))
    elif args.command == "audit":
        brief = analyze_audit(normalize_token_input(args.symbol))
    elif args.command == "meme":
        brief = analyze_meme(normalize_token_input(args.symbol))
    elif args.command == "wallet":
        brief = analyze_wallet(normalize_wallet_input(args.address))
    elif args.command == "holdings":
        target = str(getattr(args, "target", "") or "").strip()
        brief = analyze_wallet(normalize_wallet_input(target)) if target.startswith("0x") else analyze_portfolio()
    elif args.command == "signal":
        brief = analyze_signal(normalize_token_input(args.token))
    elif args.command == "portfolio":
        brief = analyze_portfolio()
    elif args.command == "watch":
        scope = str(args.scope or "today").strip().lower().replace("-", "")
        if scope not in {"today", "todays"}:
            raise SystemExit("watch currently supports only: watch today")
        brief = watch_today()
    elif args.command == "careers":
        from src.services.careers_tracker import load_snapshot, refresh_or_load, summarize_snapshot

        snapshot = load_snapshot() if args.cache_only else refresh_or_load()
        if snapshot is None:
            raise SystemExit("No local careers cache exists yet. Run without --cache-only first.")
        print(summarize_snapshot(snapshot, limit=max(args.limit, 1)))
        return
    else:
        brief = watch_today()

    print(format_brief(brief))


if __name__ == "__main__":
    main()
