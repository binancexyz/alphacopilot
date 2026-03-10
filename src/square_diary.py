from __future__ import annotations

import argparse
import json
import random
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.services.square_posts import masked_square_key, publish_square_post

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "square_diary.json"


DEFAULT_CONFIG = {
    "timezone": "Asia/Phnom_Penh",
    "morning_time": "07:30",
    "night_time": "21:30",
    "autopost": True,
    "voice": "short personal diary with builder/dev log and market thoughts",
    "custom_lines": [
        "Built around Binance Skills + OpenClaw.",
        "Less noise, better conviction.",
    ],
    "market_focus": ["BNB", "BTC", "SOL"],
}


MORNING_OPENERS = [
    "Morning diary.",
    "Good morning build note.",
    "Morning check-in.",
]

NIGHT_OPENERS = [
    "Night diary.",
    "Evening wrap-up.",
    "End-of-day note.",
]

MORNING_MARKET_LINES = [
    "Market mood this morning: stay selective, follow real signals, ignore random noise.",
    "This morning's market thought: conviction matters more than speed when headlines get loud.",
    "Quick market note: I care more about clean setups and risk control than chasing every move.",
]

NIGHT_MARKET_LINES = [
    "Tonight's market thought: the best edge is often clarity, not activity.",
    "Night market note: strong process beats reactive trading when the tape gets emotional.",
    "End-of-day market thought: clean risk framing is usually more valuable than one extra hot take.",
]


def load_config() -> dict:
    if CONFIG_PATH.exists():
        return {**DEFAULT_CONFIG, **json.loads(CONFIG_PATH.read_text(encoding="utf-8"))}
    return dict(DEFAULT_CONFIG)


def run_git(*args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return (result.stdout or "").strip()
    except Exception:
        return ""


def recent_commit_summary() -> str:
    log = run_git("log", "-3", "--pretty=%s")
    commits = [line.strip() for line in log.splitlines() if line.strip()]
    if not commits:
        return "Still building steadily behind the scenes."
    if len(commits) == 1:
        return f"Recent build progress: {commits[0]}."
    return f"Recent build progress: {commits[0]}; {commits[1]}."


def working_tree_summary() -> str:
    status = run_git("status", "--short")
    if not status:
        return "Working tree is clean right now, which is a nice feeling."
    lines = [line for line in status.splitlines() if line.strip()]
    return f"Current dev state: {len(lines)} local change(s) still in motion."


def project_line() -> str:
    return "I'm shaping Clawbot into something more useful: clearer research briefs, smoother posting, and fewer brittle steps."


def custom_line(config: dict) -> str:
    lines = [str(x).strip() for x in config.get("custom_lines", []) if str(x).strip()]
    return random.choice(lines) if lines else ""


def focus_line(config: dict, phase: str) -> str:
    focus = [str(x).upper() for x in config.get("market_focus", []) if str(x).strip()]
    if not focus:
        return ""
    if phase == "morning":
        return f"Today I'm watching {', '.join(focus[:3])} for cleaner context instead of hype." 
    return f"Closing watchlist for tonight: {', '.join(focus[:3])}."



def build_post(phase: str, config: dict) -> str:
    opener = random.choice(MORNING_OPENERS if phase == "morning" else NIGHT_OPENERS)
    market_line = random.choice(MORNING_MARKET_LINES if phase == "morning" else NIGHT_MARKET_LINES)
    bits = [
        opener,
        recent_commit_summary(),
        working_tree_summary(),
        project_line(),
        focus_line(config, phase),
        market_line,
        custom_line(config),
    ]
    text = " ".join(bit.strip() for bit in bits if bit and bit.strip())
    return text[:999].rstrip()



def main() -> None:
    parser = argparse.ArgumentParser(description="Draft or publish a scheduled Binance Square diary post")
    parser.add_argument("phase", choices=["morning", "night"])
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    config = load_config()
    tz = ZoneInfo(str(config.get("timezone", DEFAULT_CONFIG["timezone"])))
    now = datetime.now(tz)
    text = build_post(args.phase, config)

    publish = args.publish or (config.get("autopost", False) and not args.dry_run)
    result = publish_square_post(text, dry_run=not publish)

    print(text)
    print()
    print(f"phase: {args.phase}")
    print(f"now: {now.isoformat()}")
    print(f"timezone: {config.get('timezone')}")
    print(f"mode: {result.mode}")
    print(f"status: {'ok' if result.ok else 'error'}")
    if publish:
        print(f"key: {masked_square_key()}")
    if result.detail:
        print(f"detail: {result.detail}")
    if result.post_url:
        print(f"post_url: {result.post_url}")
    if result.response_body:
        print(result.response_body)


if __name__ == "__main__":
    main()
