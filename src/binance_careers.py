from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.services.careers_tracker import CACHE_PATH, load_snapshot, refresh_or_load, summarize_snapshot


def main() -> None:
    parser = argparse.ArgumentParser(description="Track and summarize Binance Careers openings")
    parser.add_argument("--refresh", action="store_true", help="Try live refresh first; otherwise use refresh-or-cache behavior")
    parser.add_argument("--cache-only", action="store_true", help="Use only the local cache file")
    parser.add_argument("--limit", type=int, default=6, help="How many openings to show")
    args = parser.parse_args()

    if args.cache_only:
        snapshot = load_snapshot(CACHE_PATH)
        if snapshot is None:
            print("Binance Careers Pulse")
            print("No local careers cache exists yet.")
            print("Run: python3 src/binance_careers.py --refresh")
            return
    elif args.refresh:
        snapshot = refresh_or_load()
    else:
        snapshot = refresh_or_load()

    print(summarize_snapshot(snapshot, limit=max(args.limit, 1)))


if __name__ == "__main__":
    main()
