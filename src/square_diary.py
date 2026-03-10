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
LOG_PATH = ROOT / "tmp" / "square_post_log.jsonl"
ARTICLE_SEEDS_PATH = ROOT / "tmp" / "square_article_seeds.jsonl"
WEEKLY_RECAP_PATH = ROOT / "tmp" / "square_weekly_recap.md"

DEFAULT_CONFIG = {
    "timezone": "Asia/Phnom_Penh",
    "autopost": True,
    "market_focus": ["BNB", "BTC", "SOL"],
    "seo_keywords": ["BNB Chain", "Binance Square", "crypto", "builder", "market", "AI agents"],
    "custom_lines": [
        "Built around Binance Skills + OpenClaw.",
        "Still aiming for less noise, better conviction.",
        "The goal is simple: clearer thinking, better tools, stronger execution.",
        "Good systems should make better judgment easier, not harder.",
    ],
    "topics": [
        "BNB Chain MCP",
        "Binance Skills",
        "AI agents",
        "crypto market structure",
        "builder workflow",
        "signal and risk",
        "OpenClaw product design",
    ],
    "schedule": {
        "morning-diary": "07:30",
        "education": "09:30",
        "market": "11:30",
        "builder": "13:30",
        "ecosystem": "15:30",
        "motivation": "18:30",
        "night-diary": "21:30"
    }
}

SERIES_NAMES = {
    "morning-diary": ["Clawbot Journal", "Morning Build Notes"],
    "education": ["Market Lessons", "Better Conviction Notes"],
    "market": ["Tape Notes", "Market Signals"],
    "builder": ["Builder Notes", "Shipping Log"],
    "ecosystem": ["BNB Chain Agent Ideas", "Skills and MCP Notes"],
    "motivation": ["Discipline Notes", "Builder Momentum"],
    "night-diary": ["Clawbot Journal", "Night Wrap"],
}

VOICE_GUIDE = {
    "morning-diary": "reflective, calm, forward-looking",
    "education": "crisp, practical, useful",
    "market": "selective, sharp, risk-aware",
    "builder": "honest, technical, grounded",
    "ecosystem": "visionary, practical, BNB Chain-native",
    "motivation": "memorable, punchy, not cheesy",
    "night-diary": "earned, calm, reflective",
}

HOOKS = {
    "morning-diary": {
        "builder-confession": [
            "Morning diary: the product usually gets better through quiet fixes, not dramatic moments.",
            "Morning note: I still trust steady iteration more than hype cycles.",
        ],
        "sharp-opinion": [
            "Strong products are often built before they are fully understood.",
            "The best builder mood is calm urgency, not chaos.",
        ],
        "curiosity": [
            "What actually compounds in crypto product work is rarely the noisiest thing on the screen.",
            "The real question this morning is not what is moving, but what is worth attention.",
        ],
    },
    "education": {
        "contrarian": [
            "More information does not automatically create better decisions.",
            "A trader can consume more and still understand less.",
        ],
        "lesson": [
            "One lesson worth repeating: structure beats noise.",
            "Here is a practical lesson most people learn too late.",
        ],
        "warning": [
            "The expensive mistake is not missing information. It is trusting weak structure.",
            "Most bad decisions look reasonable before risk is framed properly.",
        ],
    },
    "market": {
        "warning": [
            "The market always gives you enough movement to justify a bad decision.",
            "Activity is everywhere today, but activity alone is not a thesis.",
        ],
        "sharp-opinion": [
            "Clean setups deserve attention. Loud setups deserve skepticism.",
            "In this market, patience is often more profitable than participation.",
        ],
        "curiosity": [
            "The most useful market question today is whether strength is real or just well-marketed.",
            "What matters today is not the loudest coin, but the strongest follow-through.",
        ],
    },
    "builder": {
        "builder-confession": [
            "Builder note: most quality gains come from fixing boring things well.",
            "Shipping gets easier when the system becomes clearer, not just bigger.",
        ],
        "sharp-opinion": [
            "A product becomes trustworthy long before it becomes impressive.",
            "The best infrastructure feels obvious only after someone did the hard work.",
        ],
        "lesson": [
            "One product lesson: users feel friction faster than teams notice it.",
            "The invisible work is often the work that makes the whole product believable.",
        ],
    },
    "ecosystem": {
        "sharp-opinion": [
            "MCP becomes more interesting when it is paired with real reusable skills.",
            "BNB Chain gets more compelling when agents can do useful work, not just talk about it.",
        ],
        "curiosity": [
            "What happens when BNB Chain agents stop rebuilding the same glue every week?",
            "The interesting question is not whether agents can connect, but whether they can stay useful.",
        ],
        "lesson": [
            "Reusable skills are leverage, not just convenience.",
            "A strong agent ecosystem is built on composable capabilities, not prompt theater.",
        ],
    },
    "motivation": {
        "builder-confession": [
            "Some of the best progress starts on days when the work still feels messy.",
            "Momentum usually belongs to the people who keep showing up before it looks glamorous.",
        ],
        "sharp-opinion": [
            "Discipline is still one of the cleanest edges in crypto.",
            "Consistency keeps winning long after excitement fades.",
        ],
        "warning": [
            "Waiting for perfect conditions is one of the cleanest ways to stay stuck.",
            "If you need ideal conditions to begin, you will begin too late.",
        ],
    },
    "night-diary": {
        "builder-confession": [
            "Night diary: real progress still feels quiet while it is happening.",
            "Evening note: the work compounds before the credit does.",
        ],
        "lesson": [
            "The day usually teaches more when you review it calmly.",
            "One honest end-of-day lesson: clarity is earned, not assumed.",
        ],
        "sharp-opinion": [
            "A good day is not measured by noise. It is measured by signal.",
            "What deserves respect is not volume of effort, but quality of progress.",
        ],
    },
}

BODY_BANK = {
    "morning-diary": [
        [
            "I want the day to start with clean priorities, useful output, and less wasted motion.",
            "The goal is not to do everything. It is to sharpen the right things.",
        ],
        [
            "I care a lot more about clarity than activity right now.",
            "Better systems make better judgment easier, which is still one of the main goals behind this project.",
        ],
    ],
    "education": [
        [
            "Good research workflows matter because raw dashboards, hot takes, and alerts can still leave people confused.",
            "The real edge is turning scattered data into a clear decision process: signal, risk, liquidity, and invalidation.",
        ],
        [
            "A cleaner checklist can save more money than a louder signal source.",
            "The missing layer in a lot of crypto research is not data. It is interpretation.",
        ],
        [
            "Fast rejection is part of good analysis.",
            "Not every trending token deserves deep research, and not every strong story has strong structure underneath it.",
        ],
    ],
    "market": [
        [
            "There is always enough movement to create FOMO, but not every move deserves attention.",
            "Right now I care more about liquidity, confirmation, and whether strength is actually sustainable than about chasing noise.",
        ],
        [
            "Good market days reward clarity and messy days punish impatience.",
            "If the idea only works when risk is ignored, it is probably not that strong.",
        ],
        [
            "I keep coming back to the same question: did strength hold up when attention rotated?",
            "That answer matters more than timeline excitement.",
        ],
    ],
    "builder": [
        [
            "Most product work is not one giant breakthrough.",
            "It is dozens of small fixes that make the system calmer, sharper, and more trustworthy.",
        ],
        [
            "Cleaner extraction, fewer brittle paths, better defaults, and tighter loops do not look flashy, but they compound.",
            "That is how rough tools become dependable.",
        ],
        [
            "A lot of the real craft is reducing friction, ambiguity, and failure points.",
            "Users feel quality long before they can explain it.",
        ],
    ],
    "ecosystem": [
        [
            "BNB Chain MCP + skills feels like the right direction for practical agent infrastructure.",
            "If agents can plug into reusable chain-native skills instead of rebuilding the same glue every time, the user experience gets much better.",
        ],
        [
            "Reusable skills shorten the path from idea to working agent.",
            "That means builders can spend more time on product quality and less time on repetitive integration work.",
        ],
        [
            "I am especially interested in workflows around BNB Chain MCP, bnbchain-skills, and visible agent identity via 8004scan.",
            "That stack feels promising because it connects capability, distribution, and trust.",
        ],
    ],
    "motivation": [
        [
            "Start with rough tools, small wins, and one clear improvement at a time.",
            "In crypto, noise is everywhere. Discipline is the edge.",
        ],
        [
            "Strong products are rarely born polished.",
            "They become sharp because someone kept learning, fixing, and refusing to drift.",
        ],
        [
            "Consistency is underrated alpha.",
            "The compounding usually starts before the recognition does.",
        ],
    ],
    "night-diary": [
        [
            "Today reminded me that real progress is usually quiet, cumulative, and earned.",
            "What matters most is whether the system got clearer and more useful.",
        ],
        [
            "I would rather end the day with cleaner thinking than louder output.",
            "That usually ages better in both markets and product work.",
        ],
    ],
}

CTA_BANK = {
    "education": [
        "What is one research habit that improved your decisions the most?",
        "Which part of your process catches weak ideas early?",
    ],
    "market": [
        "What are you watching most closely right now: liquidity, narrative, or confirmation?",
        "What matters more to you today: strength, follow-through, or risk clarity?",
    ],
    "builder": [
        "What is one invisible product improvement you think users feel immediately?",
        "What is the most underrated part of shipping clean tools?",
    ],
    "ecosystem": [
        "What BNB Chain skill would make an agent genuinely more useful?",
        "Which matters more for agent ecosystems: better protocols or better reusable skills?",
    ],
    "motivation": [
        "What has compounded more for you lately: discipline or inspiration?",
        "What small improvement are you shipping next?",
    ],
}

SEO_ENDINGS = [
    "#BNBChain #BinanceSquare #Crypto",
    "#Crypto #BNBChain #Builders",
    "#AIAgents #BNBChain #BinanceSquare",
    "#CryptoEducation #BNBChain #Builders",
]

BANNED_FRAGMENTS = {
    "very strong direction",
    "actually worth using",
    "the future of",
    "game changer",
    "next big thing",
    "revolutionary",
}


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
    return {
        "recent_hooks": [],
        "recent_lines": [],
        "recent_posts": [],
        "recent_topics": [],
        "recent_ctas": [],
        "recent_series": [],
        "recent_hook_types": [],
    }


def save_state(state: dict[str, Any]) -> None:
    ensure_tmp_dir()
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def remember(state: dict[str, Any], key: str, value: str, limit: int = 12) -> None:
    items = [x for x in state.get(key, []) if x != value]
    items.insert(0, value)
    state[key] = items[:limit]


def append_jsonl(path: Path, item: dict[str, Any]) -> None:
    ensure_tmp_dir()
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(item, ensure_ascii=False) + "\n")


def run_git(*args: str) -> str:
    try:
        result = subprocess.run(["git", *args], cwd=ROOT, check=False, capture_output=True, text=True, timeout=10)
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


def focus_line(config: dict, prefix: str = "Watching") -> str:
    focus = [str(x).upper() for x in config.get("market_focus", []) if str(x).strip()]
    return f"{prefix} {', '.join(focus[:3])}." if focus else ""


def pick_fresh(options: list[str], seen: list[str]) -> str:
    fresh = [opt for opt in options if opt not in seen]
    pool = fresh or options
    return random.choice(pool)


def pick_topic(config: dict, state: dict[str, Any]) -> str:
    topics = [str(x).strip() for x in config.get("topics", []) if str(x).strip()]
    if not topics:
        return "BNB Chain MCP"
    topic = pick_fresh(topics, state.get("recent_topics", []))
    remember(state, "recent_topics", topic)
    return topic


def custom_line(config: dict, state: dict[str, Any]) -> str:
    lines = [str(x).strip() for x in config.get("custom_lines", []) if str(x).strip()]
    if not lines:
        return ""
    line = pick_fresh(lines, state.get("recent_lines", []))
    remember(state, "recent_lines", line)
    return line


def pick_series(slot: str, state: dict[str, Any]) -> str:
    series = pick_fresh(SERIES_NAMES.get(slot, ["Bibipilot Notes"]), state.get("recent_series", []))
    remember(state, "recent_series", series)
    return series


def pick_hook(slot: str, state: dict[str, Any]) -> tuple[str, str]:
    slot_hooks = HOOKS.get(slot, {"default": ["Post update."]})
    hook_type = pick_fresh(list(slot_hooks.keys()), state.get("recent_hook_types", []))
    remember(state, "recent_hook_types", hook_type)
    hook = pick_fresh(slot_hooks[hook_type], state.get("recent_hooks", []))
    remember(state, "recent_hooks", hook)
    return hook_type, hook


def pick_body(slot: str, topic: str) -> list[str]:
    variants = BODY_BANK.get(slot, [])
    chosen = list(random.choice(variants)) if variants else []
    if slot == "ecosystem":
        chosen.append(f"Right now the topic I keep coming back to is {topic}.")
    elif slot == "education":
        chosen.append(f"That is exactly why topics like {topic} deserve clearer workflows, not just more content.")
    elif slot == "builder":
        chosen.append(f"That mindset matters a lot when building around {topic}.")
    return chosen


def pick_cta(slot: str, state: dict[str, Any]) -> str:
    options = CTA_BANK.get(slot, [])
    if not options:
        return ""
    cta = pick_fresh(options, state.get("recent_ctas", []))
    remember(state, "recent_ctas", cta)
    return cta


def seo_tail(config: dict, topic: str) -> str:
    keywords = [str(x).strip() for x in config.get("seo_keywords", []) if str(x).strip()]
    tags = random.choice(SEO_ENDINGS)
    lead = random.choice(keywords) if keywords else topic
    return f"{lead}, {topic}. {tags}"


def post_too_similar(text: str, state: dict[str, Any]) -> bool:
    for recent in state.get("recent_posts", [])[:6]:
        overlap = len(set(text.lower().split()) & set(recent.lower().split()))
        if overlap >= 26:
            return True
    return False


def cringe_filter(text: str, state: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    lower = text.lower()
    for fragment in BANNED_FRAGMENTS:
        if fragment in lower:
            issues.append(f"banned phrase: {fragment}")
    if len(text) < 220:
        issues.append("too short")
    if len(text) > 950:
        issues.append("too long")
    if text.count("#") > 3:
        issues.append("too many hashtags")
    if post_too_similar(text, state):
        issues.append("too similar to recent post")
    return issues


def build_post(slot: str, config: dict, state: dict[str, Any]) -> tuple[str, dict[str, str]]:
    topic = pick_topic(config, state)
    series = pick_series(slot, state)
    hook_type, hook = pick_hook(slot, state)
    bits = [f"{series}: {hook}"]

    if slot == "morning-diary":
        bits.extend(
            [
                *pick_body(slot, topic),
                recent_commit_summary(),
                working_tree_summary(),
                focus_line(config, "Today I'm watching"),
                custom_line(config, state),
            ]
        )
    elif slot == "night-diary":
        bits.extend(
            [
                *pick_body(slot, topic),
                recent_commit_summary(),
                working_tree_summary(),
                focus_line(config, "Closing watchlist:"),
                custom_line(config, state),
            ]
        )
    elif slot == "market":
        bits.extend([*pick_body(slot, topic), focus_line(config), custom_line(config, state), pick_cta(slot, state)])
    elif slot == "builder":
        bits.extend([*pick_body(slot, topic), recent_commit_summary(), working_tree_summary(), pick_cta(slot, state)])
    elif slot == "ecosystem":
        bits.extend([*pick_body(slot, topic), custom_line(config, state), pick_cta(slot, state)])
    elif slot == "motivation":
        bits.extend([*pick_body(slot, topic), custom_line(config, state), pick_cta(slot, state)])
    else:
        bits.extend([*pick_body(slot, topic), custom_line(config, state), pick_cta(slot, state)])

    bits.append(seo_tail(config, topic))
    text = " ".join(bit.strip() for bit in bits if bit and bit.strip())
    text = text[:999].rstrip()

    meta = {
        "slot": slot,
        "topic": topic,
        "series": series,
        "hook_type": hook_type,
        "voice": VOICE_GUIDE.get(slot, "clear"),
    }
    return text, meta


def generate_post(slot: str, config: dict, state: dict[str, Any]) -> tuple[str, dict[str, str], list[str]]:
    last_text = ""
    last_meta: dict[str, str] = {}
    last_issues: list[str] = []
    for _ in range(8):
        text, meta = build_post(slot, config, state)
        issues = cringe_filter(text, state)
        last_text, last_meta, last_issues = text, meta, issues
        if not issues:
            return text, meta, issues
    return last_text, last_meta, last_issues


def save_article_seed(now: datetime, meta: dict[str, str], text: str) -> None:
    if meta.get("slot") not in {"education", "ecosystem", "builder"}:
        return
    seed = {
        "timestamp": now.isoformat(),
        "slot": meta.get("slot"),
        "topic": meta.get("topic"),
        "series": meta.get("series"),
        "title": f"Expand: {meta.get('series')} — {meta.get('topic')}",
        "seed_text": text,
    }
    append_jsonl(ARTICLE_SEEDS_PATH, seed)


def refresh_weekly_recap() -> None:
    if not LOG_PATH.exists():
        return
    lines = [json.loads(line) for line in LOG_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    recent = lines[-20:]
    if not recent:
        return
    topics: dict[str, int] = {}
    slots: dict[str, int] = {}
    for item in recent:
        topics[item.get("topic", "unknown")] = topics.get(item.get("topic", "unknown"), 0) + 1
        slots[item.get("slot", "unknown")] = slots.get(item.get("slot", "unknown"), 0) + 1
    top_topics = sorted(topics.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
    top_slots = sorted(slots.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
    content = [
        "# Binance Square Weekly Recap\n",
        "## Recent posting mix\n",
        *[f"- {slot}: {count}\n" for slot, count in top_slots],
        "\n## Top recurring topics\n",
        *[f"- {topic}: {count}\n" for topic, count in top_topics],
        "\n## Latest post links\n",
    ]
    for item in recent[-5:]:
        if item.get("post_url"):
            content.append(f"- {item['slot']} — {item['post_url']}\n")
    WEEKLY_RECAP_PATH.write_text("".join(content), encoding="utf-8")


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
    text, meta, issues = generate_post(args.slot, config, state)
    publish = args.publish or (config.get("autopost", False) and not args.dry_run)
    if issues and publish:
        result = publish_square_post("", dry_run=True)
        result.ok = False
        result.detail = f"Blocked by quality filter: {', '.join(issues)}"
    else:
        result = publish_square_post(text, dry_run=not publish)

    if result.ok:
        remember(state, "recent_posts", text, limit=20)
        save_state(state)
        append_jsonl(
            LOG_PATH,
            {
                "timestamp": now.isoformat(),
                "slot": meta.get("slot"),
                "topic": meta.get("topic"),
                "series": meta.get("series"),
                "hook_type": meta.get("hook_type"),
                "voice": meta.get("voice"),
                "mode": result.mode,
                "post_url": result.post_url,
                "text": text,
            },
        )
        save_article_seed(now, meta, text)
        refresh_weekly_recap()

    print(text)
    print()
    print(f"slot: {args.slot}")
    print(f"topic: {meta.get('topic')}")
    print(f"series: {meta.get('series')}")
    print(f"hook_type: {meta.get('hook_type')}")
    print(f"voice: {meta.get('voice')}")
    print(f"now: {now.isoformat()}")
    print(f"timezone: {config.get('timezone')}")
    print(f"mode: {result.mode}")
    print(f"status: {'ok' if result.ok else 'error'}")
    if issues:
        print(f"quality_issues: {', '.join(issues)}")
    if publish and result.ok:
        print(f"key: {masked_square_key()}")
    if result.detail:
        print(f"detail: {result.detail}")
    if result.post_url:
        print(f"post_url: {result.post_url}")
    if result.response_body:
        print(result.response_body)


if __name__ == "__main__":
    main()
