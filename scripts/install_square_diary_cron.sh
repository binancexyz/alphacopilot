#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$ROOT/tmp"
mkdir -p "$LOG_DIR"

slots=(
  "07:30|morning-diary"
  "09:30|education-1"
  "11:30|market-1"
  "13:30|builder-1"
  "15:30|ecosystem-1"
  "18:30|motivation-1"
  "21:30|night-diary"
)

EXISTING="$(crontab -l 2>/dev/null | grep -v 'src/square_diary.py' || true)"
{
  printf 'CRON_TZ=Asia/Phnom_Penh\n'
  if [[ -n "$EXISTING" ]]; then
    printf '%s\n' "$EXISTING"
  fi
  for item in "${slots[@]}"; do
    time="${item%%|*}"
    slot="${item##*|}"
    hour="${time%%:*}"
    minute="${time##*:}"
    printf '%s %s * * * cd %s && . .venv/bin/activate && set -a && . .env && set +a && python src/square_diary.py %s --publish >> %s/square-%s.log 2>&1\n' "$minute" "$hour" "$ROOT" "$slot" "$LOG_DIR" "$slot"
  done
} | crontab -

echo "Installed Binance Square schedule:"
crontab -l | grep 'src/square_diary.py' || true
