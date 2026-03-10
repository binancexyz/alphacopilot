#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

if [[ ! -f .env ]]; then
  echo "Missing .env. Create it from .env.local.template first."
  exit 1
fi

echo "Check these .env values before live use:"
echo "- APP_MODE=live"
echo "- BINANCE_SKILLS_BASE_URL set if using live market/runtime adapter"
echo "- BINANCE_SQUARE_API_KEY set"
echo "- BINANCE_SQUARE_API_BASE_URL set"
echo "- BINANCE_SQUARE_API_PUBLISH_PATH set correctly"
echo "- BINANCE_SQUARE_API_KEY_HEADER set correctly"
echo
echo "Current non-empty keys in .env:"
grep -E '^[A-Z0-9_]+=.+$' .env | sed 's/=.*$/=<set>/'
