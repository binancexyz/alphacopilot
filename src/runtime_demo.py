from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.services.runtime_bridge_live_stub import (  # noqa: E402
    signal_from_raw,
    token_from_raw,
    wallet_from_raw,
    watchtoday_from_raw,
)


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    parser = argparse.ArgumentParser(description="Runtime payload demo for Bibipilot")
    sub = parser.add_subparsers(dest="command", required=True)

    p_token = sub.add_parser("token")
    p_token.add_argument("symbol")
    p_token.add_argument("payload")

    p_signal = sub.add_parser("signal")
    p_signal.add_argument("token")
    p_signal.add_argument("payload")

    p_wallet = sub.add_parser("wallet")
    p_wallet.add_argument("address")
    p_wallet.add_argument("payload")

    p_watch = sub.add_parser("watchtoday")
    p_watch.add_argument("payload")

    args = parser.parse_args()
    raw = load_json(args.payload)

    if args.command == "token":
        print(token_from_raw(args.symbol, raw))
    elif args.command == "signal":
        print(signal_from_raw(args.token, raw))
    elif args.command == "wallet":
        print(wallet_from_raw(args.address, raw))
    else:
        print(watchtoday_from_raw(raw))


if __name__ == "__main__":
    main()
