from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.analyzers.audit_analysis import analyze_audit
from src.analyzers.market_watch import watch_today
from src.analyzers.meme_analysis import analyze_meme
from src.analyzers.signal_check import analyze_signal
from src.analyzers.token_analysis import analyze_token
from src.analyzers.wallet_analysis import analyze_wallet
from src.services.square_posts import build_square_post, masked_square_key, publish_square_post
from src.utils.parsing import normalize_token_input, normalize_wallet_input


def main() -> None:
    parser = argparse.ArgumentParser(description="Draft or publish Binance Square posts")
    sub = parser.add_subparsers(dest="command", required=True)

    token = sub.add_parser("token")
    token.add_argument("symbol")
    token.add_argument("--publish", action="store_true")

    signal = sub.add_parser("signal")
    signal.add_argument("token")
    signal.add_argument("--publish", action="store_true")

    audit = sub.add_parser("audit")
    audit.add_argument("symbol")
    audit.add_argument("--publish", action="store_true")

    meme = sub.add_parser("meme")
    meme.add_argument("symbol")
    meme.add_argument("--publish", action="store_true")

    wallet = sub.add_parser("wallet")
    wallet.add_argument("address")
    wallet.add_argument("--publish", action="store_true")

    watch = sub.add_parser("watchtoday")
    watch.add_argument("--publish", action="store_true")

    args = parser.parse_args()

    if args.command == "token":
        brief = analyze_token(normalize_token_input(args.symbol))
        publish = args.publish
    elif args.command == "signal":
        brief = analyze_signal(normalize_token_input(args.token))
        publish = args.publish
    elif args.command == "audit":
        brief = analyze_audit(normalize_token_input(args.symbol))
        publish = args.publish
    elif args.command == "meme":
        brief = analyze_meme(normalize_token_input(args.symbol))
        publish = args.publish
    elif args.command == "wallet":
        brief = analyze_wallet(normalize_wallet_input(args.address))
        publish = args.publish
    else:
        brief = watch_today()
        publish = args.publish

    text = build_square_post(brief)
    result = publish_square_post(text, dry_run=not publish)

    print(text)
    print()
    print(f"mode: {result.mode}")
    print(f"status: {'ok' if result.ok else 'error'}")
    if publish:
        print(f"key: {masked_square_key()}")
    if result.detail:
        print(f"detail: {result.detail}")
    if result.post_url:
        print(f"post_url: {result.post_url}")
    if result.response_body:
        print(result.response_body)


if __name__ == "__main__":
    main()
