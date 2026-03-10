from __future__ import annotations

import argparse
import json
import random
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.services.square_posts import masked_square_key, publish_square_post

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "square_diary.json"
STATE_PATH = ROOT / "tmp" / "square_diary_state.json"

DEFAULT_CONFIG = {
    "timezone": "Asia/Phnom_Penh",
    "autopost": True,
    "market_focus": ["BNB", "BTC", "SOL"],
    "seo_keywords": ["BNB Chain", "Binance Square", "crypto", "builder", "market", "AI agents"],
    "custom_lines": [
        "Built around Binance Skills + OpenClaw.",
        "Still aiming for less noise, better conviction.",
        "The goal is simple: clearer thinking, better tools, stronger execution.",
    ],
    "schedule": {
        "morning-diary": "07:30",
        "education-1": "09:00",
        "market-open": "10:30",
        "builder-1": "12:00",
        "ecosystem-1": "13:30",
        "education-2": "15:00",
        "market-close": "16:30",
        "motivation-1": "18:00",
        "builder-2": "19:30",
        "night-diary": "21:30"
    }
}

HOOKS = {
    "morning-diary": [
        "Morning diary.",
        "Good morning build note.",
        "Morning check-in.",
        "New day, same mission: build something sharper.",
    ],
    "night-diary": [
        "Night diary.",
        "Evening wrap-up.",
        "End-of-day note.",
        "Quiet progress report for tonight.",
    ],
    "education-1": [
        "Quick education post.",
        "Short lesson for today.",
        "Education note.",
        "One useful idea for builders and traders.",
    ],
    "education-2": [
        "Second education note for today.",
        "Another practical lesson.",
        "Useful reminder.",
        "Here is the part many people skip.",
    ],
    "market-open": [
        "Market open thought.",
        "Today's market setup.",
        "Current market take.",
        "If I had to summarize the tape in one line.",
    ],
    "market-close": [
        "Late-day market reflection.",
        "Closing market thought.",
        "Market wrap-up note.",
        "What the market is teaching today.",
    ],
    "builder-1": [
        "Builder log.",
        "Dev update.",
        "Product thought.",
        "A small builder note.",
    ],
    "builder-2": [
        "Second builder note.",
        "Shipping thought.",
        "Evening builder log.",
        "Another product lesson from the trenches.",
    ],
    "ecosystem-1": [
        "Ecosystem note.",
        "BNB Chain / skills thought.",
        "Infra thought.",
        "One ecosystem idea worth watching.",
    ],
    "motivation-1": [
        "Motivation post.",
        "Builder reminder.",
        "Discipline note.",
        "For anyone building through messy conditions.",
    ],
}

BODY_BANK = {
    "education-1": [
        [
            "Crypto lesson: information is not the same as judgment.",
            "Good workflows matter because raw dashboards, hot takes, and alerts can still leave people confused.",
            "The real edge is turning scattered data into a clear decision process: signal, risk, liquidity, and invalidation.",
        ],
        [
            "A lot of people consume more data and still make worse decisions.",
            "The missing layer is structure: what matters, what is noise, and what would change your view.",
            "Better frameworks usually beat more tabs.",
        ],
    ],
    "education-2": [
        [
            "One underrated skill in crypto is learning how to say no quickly.",
            "Not every trending coin deserves deep research, and not every strong story has strong structure underneath it.",
            "Fast rejection is part of good analysis.",
        ],
        [
            "Education matters because most mistakes are not technical — they are emotional and process-driven.",
            "People often confuse movement with opportunity and speed with conviction.",
            "A cleaner checklist can save more money than a louder signal source.",
        ],
    ],
    "market-open": [
        [
            "Market today feels like a reminder to stay selective.",
            "There is always enough movement to create FOMO, but not every move deserves attention.",
            "Right now I care more about liquidity, confirmation, and whether strength is actually sustainable than about chasing noise.",
        ],
        [
            "The market is active, but activity alone is not a thesis.",
            "I want to see clean structure, strong follow-through, and risk that actually makes sense.",
            "Noise is cheap. Clarity is expensive.",
        ],
    ],
    "market-close": [
        [
            "Late-day market thought: good days reward clarity and messy days punish impatience.",
            "If the move only works when you ignore risk, it probably is not that strong.",
            "I would rather miss a weak trade than force a bad one.",
        ],
        [
            "By the end of the day, the market usually tells you whether the narrative had real depth or just volume.",
            "I keep coming back to the same question: did strength hold up when attention rotated?",
            "That answer matters more than social hype.",
        ],
    ],
    "builder-1": [
        [
            "Most product work is not one giant breakthrough.",
            "It is dozens of small fixes that make the system calmer, sharper, and more trustworthy.",
            "That is where real quality usually comes from.",
        ],
        [
            "The work I respect most is usually invisible from the outside.",
            "Cleaner extraction, fewer brittle paths, better defaults, and tighter loops do not look flashy, but they compound.",
            "That is how rough tools become dependable.",
        ],
    ],
    "builder-2": [
        [
            "Builder note: shipping is not just about adding features.",
            "A lot of the real craft is reducing friction, ambiguity, and failure points.",
            "Users feel quality long before they can explain it.",
        ],
        [
            "The more I build, the more I care about systems that stay useful under pressure.",
            "Anyone can make a demo look smart. The hard part is making the product stay useful when inputs get messy.",
            "That is the standard worth chasing.",
        ],
    ],
    "ecosystem-1": [
        [
            "BNB Chain MCP + skills feels like the right direction for practical agent infrastructure.",
            "If agents can plug into reusable chain-native skills instead of rebuilding the same glue every time, the user experience gets much better.",
            "I am especially interested in workflows around BNB Chain MCP, bnbchain-skills, and visible agent identity via 8004scan.",
        ],
        [
            "The interesting part of the BNB Chain skills ecosystem is not just tooling — it is leverage.",
            "Reusable skills shorten the path from idea to working agent, which means builders can spend more time on product quality and less on repetitive integration work.",
            "That is how ecosystems become real force multipliers.",
        ],
    ],
    "motivation-1": [
        [
            "Builder reminder: you do not need perfect conditions to make meaningful progress.",
            "Start with rough tools, small wins, and one clear improvement at a time.",
            "In crypto, noise is everywhere. Discipline is the edge. Keep building.",
        ],
        [
            "Some of the best momentum comes from showing up on days when the work still feels messy.",
            "Strong products are rarely born polished. They become sharp because someone kept learning, fixing, and refusing to drift.",
            "Consistency is underrated alpha.",
        ],
    ],
}

SEO_ENDINGS = [
    "#BNBChain #BinanceSquare #Crypto",
    "#Crypto #BNBChain #Builders",
    "#MarketThoughts #BNBChain #AI",
    "#CryptoEducation #BinanceSquare #BNBChain",
]


def ensure_tmp_dir() -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    if CONFIG_PATH.exists():
        return {**DEFAULT_CONFIG, **json.loads(CONFIG_PATH.read_text(encoding="utf-8"))}
    return dict(DEFAULT_CONFIG)


def load_state() -> dict[str, Any]:
    ensure_tmp_dir()
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"recent_hooks": [], "recent_lines": [], "recent_posts": []}


def save_state(state: dict[str, Any]) -> None:
    ensure_tmp_dir()
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def remember(state: dict[str, Any], key: str, value: str, limit: int = 12) -> None:
    items = [x for x in state.get(key, []) if x != value]
    items.insert(0, value)
    state[key] = items[:limit]


def run_git(*args: str) -> str:
    try:
        result = subprocess.run(["git", *args], cwd=ROOT, check=False, capture_output=True, text=True, timeout=10)
        return (result.stdout or "").strip()
    except Exception:
        return ""


def recent_commit_summary() -> str:
    log = run_git("log", "-4", "--pretty=%s")
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


def focus_line(config: dict, prefix: str = "Watching") -> str:
    focus = [str(x).upper() for x in config.get("market_focus", []) if str(x).strip()]
    return f"{prefix} {', '.join(focus[:3])}." if focus else ""


def pick_fresh(options: list[str], seen: list[str]) -> str:
    fresh = [opt for opt in options if opt not in seen]
    pool = fresh or options
    return random.choice(pool)


def custom_line(config: dict, state: dict[str, Any]) -> str:
    lines = [str(x).strip() for x in config.get("custom_lines", []) if str(x).strip()]
    if not lines:
        return ""
    line = pick_fresh(lines, state.get("recent_lines", []))
    remember(state, "recent_lines", line)
    return line


def project_line() -> str:
    return "I'm shaping Clawbot into something more useful: clearer research briefs, smoother posting, and fewer brittle steps."


def pick_hook(slot: str, state: dict[str, Any]) -> str:
    hook = pick_fresh(HOOKS.get(slot, ["Post update."]), state.get("recent_hooks", []))
    remember(state, "recent_hooks", hook)
    return hook


def pick_body(slot: str) -> list[str]:
    variants = BODY_BANK.get(slot, [])
    return random.choice(variants) if variants else []


def seo_tail(config: dict) -> str:
    keywords = [str(x).strip() for x in config.get("seo_keywords", []) if str(x).strip()]
    tags = random.choice(SEO_ENDINGS)
    if not keywords:
        return tags
    lead = random.choice(keywords)
    return f"{lead}. {tags}"


def build_post(slot: str, config: dict, state: dict[str, Any]) -> str:
    opener = pick_hook(slot, state)

    if slot == "morning-diary":
        bits = [
            opener,
            recent_commit_summary(),
            working_tree_summary(),
            project_line(),
            focus_line(config, "Today I'm watching"),
            "Quick market note: I care more about clean setups and risk control than chasing every move.",
            custom_line(config, state),
            seo_tail(config),
        ]
    elif slot == "night-diary":
        bits = [
            opener,
            recent_commit_summary(),
            working_tree_summary(),
            "Today reminded me that real progress is usually quiet, cumulative, and earned.",
            focus_line(config, "Closing watchlist for tonight:"),
            "End-of-day market thought: clean risk framing is usually more valuable than one extra hot take.",
            custom_line(config, state),
            seo_tail(config),
        ]
    elif slot in BODY_BANK:
        bits = [opener, *pick_body(slot)]
        if slot in {"builder-1", "builder-2"}:
            bits.extend([recent_commit_summary(), working_tree_summary()])
        if slot in {"market-open", "market-close"}:
            bits.append(focus_line(config))
        bits.extend([custom_line(config, state), seo_tail(config)])
    else:
        bits = [opener, custom_line(config, state), seo_tail(config)]

    text = " ".join(bit.strip() for bit in bits if bit and bit.strip())
    return text[:999].rstrip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Draft or publish a scheduled Binance Square post")
    parser.add_argument("slot", choices=list(DEFAULT_CONFIG["schedule"].keys()))
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    config = load_config()
    state = load_state()
    tz = ZoneInfo(str(config.get("timezone", DEFAULT_CONFIG["timezone"])))
    now = datetime.now(tz)
    text = build_post(args.slot, config, state)
    publish = args.publish or (config.get("autopost", False) and not args.dry_run)
    result = publish_square_post(text, dry_run=not publish)

    if result.ok:
        remember(state, "recent_posts", text, limit=20)
        save_state(state)

    print(text)
    print()
    print(f"slot: {args.slot}")
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
