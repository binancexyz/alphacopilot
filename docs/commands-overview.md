# Commands Overview

## Live command surface

### `/brief <symbol>`
**Purpose:** Default asset read.
- Fast by default
- Can go deeper when richer asset context is available
- Absorbs the older `/token` role over time

**Examples:**
- `python3 src/main.py brief BTC`
- `python3 src/main.py brief BNB deep`

---

### `/signal <symbol>`
**Purpose:** Setup judgment.
- Signal quality
- Risks
- Invalidation
- Better canonical home for the old `/risk` surface

**Example:** `python3 src/main.py signal DOGE`

---

### `/audit <symbol>`
**Purpose:** Safety read.
- Contract/security posture
- Audit gate
- Risk level
- Meme lens folded into findings/context when useful

**Example:** `python3 src/main.py audit BNB`

---

### `/holdings [address]`
**Purpose:** Unified posture read.
- No argument → your private Binance Spot posture
- Address argument → public wallet behavior read
- One command for ownership/posture intelligence
- Current product promise: posture + analytics + Alpha exposure

**Examples:**
- `python3 src/main.py holdings`
- `python3 src/main.py holdings 0x1234567890ab`

---

### `/watchtoday`
**Purpose:** Daily market board.
- Prioritized narratives
- Smart-money context
- Selective ranking
- Front-page market view

**Example:** `python3 src/main.py watchtoday`

---

## Compatibility commands
These are legacy, folded, or supporting surfaces rather than the public command map.

- `/alpha [symbol]` → supporting Binance Alpha read; not part of the main public surface
- `/futures <symbol>` → supporting futures positioning read; not part of the main public surface

- `/token <symbol>` → use `/brief <symbol> deep`
- `/portfolio` → use `/holdings`
- `/wallet <address>` → use `/holdings <address>`
- `/risk <symbol>` → use `/signal <symbol>`
- `/meme <symbol>` → use `/audit <symbol>`
- `/price <symbol>` → hidden utility surface
- `careers` → removed from main product surface
- `/watch` → removed alias

---

## Product grouping
- **Research** → `/brief`, `/watchtoday`
- **Judgment** → `/signal`, `/audit`
- **Posture** → `/holdings`

---

## Output shape
- Structured section-based layout
- Explicit live-trust labeling (`✅ Live now`, `🟡 Partial live / degraded`, `🔴 Mock / not live`)
- Read / Verdict / Risks / Watch blocks where appropriate
- Context / Source / Validity tags when relevant
- Explicit invalidation in `/signal`
- Premium tree-style hierarchy for grouped outputs
