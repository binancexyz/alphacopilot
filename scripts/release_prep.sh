#!/usr/bin/env bash
set -euo pipefail

make check
make test
scripts/demo_capture.sh > /tmp/bibipilot-demo.txt

echo "Release prep complete."
echo "Demo output exported to /tmp/bibipilot-demo.txt"
