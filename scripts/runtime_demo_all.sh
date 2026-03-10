#!/usr/bin/env bash
set -euo pipefail

python3 src/runtime_demo.py token BNB examples/payloads/token-bnb.json
printf '\n---\n\n'
python3 src/runtime_demo.py signal DOGE examples/payloads/signal-doge.json
printf '\n---\n\n'
python3 src/runtime_demo.py wallet 0x1234567890ab examples/payloads/wallet-sample.json
printf '\n---\n\n'
python3 src/runtime_demo.py watchtoday examples/payloads/watchtoday-sample.json
