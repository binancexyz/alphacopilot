#!/usr/bin/env bash
set -euo pipefail

python3 src/main.py token BNB
printf '\n---\n\n'
python3 src/main.py signal DOGE
printf '\n---\n\n'
python3 src/main.py wallet 0x1234567890ab
printf '\n---\n\n'
python3 src/main.py watchtoday
