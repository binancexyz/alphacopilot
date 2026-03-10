#!/usr/bin/env bash
set -euo pipefail

make check
make test
scripts/demo_capture.sh > /tmp/alphacopilot-demo.txt

echo "Release prep complete."
echo "Demo output exported to /tmp/alphacopilot-demo.txt"
