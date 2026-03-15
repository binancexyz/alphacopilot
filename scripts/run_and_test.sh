#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

if [[ ! -d .venv ]]; then
  echo "Missing .venv. Run scripts/setup_local_env.sh first."
  exit 1
fi

# shellcheck disable=SC1091
source .venv/bin/activate

echo "== Running checks =="
make check
make test

echo
echo "== Smoke tests =="
python3 src/main.py brief BNB | sed -n '1,20p'
echo
python3 src/main.py portfolio | sed -n '1,20p'
echo
python3 src/main.py wallet 0x1234567890ab | sed -n '1,20p'
echo
python3 src/main.py alpha | sed -n '1,20p'
echo
python3 src/main.py futures BTC | sed -n '1,20p'
echo
echo "-- Square draft --"
python3 src/square_cli.py token BNB | sed -n '1,10p'

echo
echo "== API hint =="
echo "Start API with: source .venv/bin/activate && make api"
echo "Then test: curl http://127.0.0.1:8000/health"
