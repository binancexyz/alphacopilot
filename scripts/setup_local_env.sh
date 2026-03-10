#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

echo "== Bibipilot local setup =="
echo "repo: $REPO_DIR"

echo
echo "[1/5] Checking for python3"
command -v python3 >/dev/null
python3 --version

echo
echo "[2/5] Checking for python3-venv support"
if ! python3 -m venv --help >/dev/null 2>&1; then
  echo "python3-venv support is missing. On Ubuntu/Debian run:"
  echo "  apt-get update && apt-get install -y python3.12-venv"
  exit 1
fi

echo
echo "[3/5] Creating virtual environment (.venv)"
python3 -m venv .venv

# shellcheck disable=SC1091
source .venv/bin/activate

echo
echo "[4/5] Installing requirements"
pip install --upgrade pip
pip install -r requirements.txt

echo
echo "[5/5] Preparing .env"
if [[ ! -f .env ]]; then
  cp env.local.template .env
  chmod 600 .env || true
  echo "Created .env from env.local.template"
else
  echo ".env already exists; leaving it unchanged"
fi

echo
echo "Setup complete."
echo "Next steps:"
echo "  1. Edit .env with your real values"
echo "  2. source .venv/bin/activate"
echo "  3. make check && make test"
echo "  4. make api"
