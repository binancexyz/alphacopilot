#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$ROOT/tmp"
mkdir -p "$LOG_DIR"

slots=(
  "07:30|morning-diary"
  "09:00|education-1"
  "10:30|market-open"
  "12:00|builder-1"
  "13:30|ecosystem-1"
  "15:00|education-2"
  "16:30|market-close"
  "18:00|motivation-1"
  "19:30|builder-2"
  "21:30|night-diary"
)

EXISTING="$(crontab -l 2>/dev/null | grep -v 'src/square_diary.py' | grep -v '^CRON_TZ=Asia/Phnom_Penh$' || true)"
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
