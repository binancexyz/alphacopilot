#!/usr/bin/env bash
set -euo pipefail

mkdir -p examples/generated
python3 src/main.py token BNB > examples/generated/token.txt
python3 src/main.py signal DOGE > examples/generated/signal.txt
python3 src/main.py wallet 0x1234567890ab > examples/generated/wallet.txt
python3 src/main.py watchtoday > examples/generated/watchtoday.txt

echo "Exported generated examples to examples/generated/"
