# Commands Overview

## Canonical commands

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

### `/holdings [address]`
**Purpose:** Unified posture read.
- No argument → your private Binance Spot posture
- Address argument → public wallet behavior read
- One command for ownership/posture intelligence

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

### `/audit <symbol>`
**Purpose:** Safety read.
- Contract/security posture
- Audit gate
- Risk level
- Meme lens folded into findings/context when useful

**Example:** `python3 src/main.py audit BNB`

---

## Compatibility commands
These still work, but they are no longer the public command map.

- `/token <symbol>` → use `/brief <symbol> deep`
- `/portfolio` → use `/holdings`
- `/wallet <address>` → use `/holdings <address>`
- `/risk <symbol>` → use `/signal <symbol>`
- `/meme <symbol>` → use `/audit <symbol>`
- `/price <symbol>` → hidden utility surface
- `careers` → removed from main product surface
- `/watch` → removed alias

---

## Output shape
- Structured section-based layout
- Read / Verdict / Risks / Watch blocks where appropriate
- Context / Source / Validity tags when relevant
- Explicit invalidation in `/signal`
- Premium tree-style hierarchy for grouped outputs
