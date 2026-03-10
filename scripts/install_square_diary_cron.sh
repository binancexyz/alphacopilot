#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$ROOT/tmp"
mkdir -p "$LOG_DIR"

MORNING_JOB="30 7 * * * cd $ROOT && . .venv/bin/activate && set -a && . .env && set +a && python src/square_diary.py morning --publish >> $LOG_DIR/square-diary-morning.log 2>&1"
NIGHT_JOB="30 21 * * * cd $ROOT && . .venv/bin/activate && set -a && . .env && set +a && python src/square_diary.py night --publish >> $LOG_DIR/square-diary-night.log 2>&1"

EXISTING="$(crontab -l 2>/dev/null | grep -v 'src/square_diary.py' || true)"
{
  printf 'CRON_TZ=Asia/Phnom_Penh\n'
  if [[ -n "$EXISTING" ]]; then
    printf '%s\n' "$EXISTING"
  fi
  printf '%s\n' "$MORNING_JOB"
  printf '%s\n' "$NIGHT_JOB"
} | crontab -

echo "Installed Binance Square diary cron jobs:"
crontab -l | grep 'src/square_diary.py' || true
