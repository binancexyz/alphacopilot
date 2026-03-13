#!/usr/bin/env bash
set -euo pipefail

mkdir -p examples/generated
python3 src/main.py brief BNB > examples/generated/brief.txt
python3 src/main.py brief BNB deep > examples/generated/brief-deep.txt
python3 src/main.py signal DOGE > examples/generated/signal.txt
python3 src/main.py holdings 0x1234567890ab > examples/generated/holdings-wallet.txt
python3 src/main.py holdings > examples/generated/holdings.txt
python3 src/main.py audit BNB > examples/generated/audit.txt
python3 src/main.py watchtoday > examples/generated/watchtoday.txt

echo "Exported generated examples to examples/generated/"
