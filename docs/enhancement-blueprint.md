# Bibipilot Enhancement Blueprint

A working master plan for the next phase of Bibipilot.

## Layer 1 — Output Quality

### `/brief`
- Lock verdicts to exactly two fragments.
- Add liquidity quality labels:
  - `< $1M` → `⚠️ very thin`
  - `$1M–$10M` → `⚠️ thin`
  - `$10M–$50M` → `🟡 moderate`
  - `> $50M` → `✅ deep`
- Replace free trend language with a controlled vocabulary:
  - `+3%+` → `Bullish momentum`
  - `+1–3%` → `Mild uptrend`
  - `-1% to +1%` → `Neutral drift`
  - `-1% to -3%` → `Mild downtrend`
  - `-3%+` → `Bearish pressure`
  - no data → `Defensive drift`

### `/brief deep`
- Keep a separate deep-lens verdict from normal `/brief`.
- Expand ownership block when data is rich.
- Add a depth-delta line that only deep mode earns (for example: holders growth / ownership context).
- Keep ownership visually distinct from `/holdings`; prefer `🧠 Ownership` over `💼 Top Holdings` if the block is structural rather than literal holdings.

### `/signal`
- Add entry zone from `triggerPrice ±1%` when available.
- Show exit-rate context when available.
- Show signal age with freshness marker.
- Keep invalidation on a controlled vocabulary:
  - `No smart-money follow-through`
  - `Most wallets already exited`
  - `Structural caution not resolved`
  - `Volume fails to support move`
  - `Entry above trigger zone`

### `/holdings`
- Add posture change detection using local snapshots.
- Make the verdict aware of current board conditions from `/watchtoday`.

### `/holdings <address>`
- Add rotation detection from snapshots.
- Add wallet style tag to the verdict/follow read.
- Upgrade follow quality labels:
  - `⚠️ Untrackable — insufficient history`
  - `🟡 Watchable — early pattern emerging`
  - `🟢 Trackable — consistent behavior visible`

### `/watchtoday`
- Show signal age per signal row.
- Add liquidity quality flags to attention rows using the same `/brief` liquidity system.
- Use a controlled board-verdict vocabulary:
  - `Strong board. High selectivity needed.`
  - `Moderate board. Be selective.`
  - `Signal-led day. Low noise.`
  - `Hype day. Caution.`
  - `Quiet board. Hold posture.`

### `/audit`
- Add structured check-count style findings.
- Make meme-lens trigger logic more explicit.
- Make gate rationale visible inside the verdict.

## Layer 2 — System Architecture

### Thin-data handling
Formalize four runtime states:
1. `Full data ✅`
2. `Partial data 🟡`
3. `Thin data 🟠`
4. `No data ⚪`

Each state should drive:
- how many fields render
- whether values become `—`
- maximum verdict confidence
- footer fallback wording

### Snapshot system
Store lightweight snapshots with:
- timestamp
- symbol or address
- price / liquidity / holdings / signal status / concentration

Retention targets:
- `/brief` → 24h
- `/signal` → 48h
- `/holdings` → 7 days

Unlocks:
- posture change detection
- wallet rotation detection
- trend confirmation
- signal staleness

### Skill-call optimization
Parallelize independent skill calls where possible.

### Per-skill error recovery
Use command-specific fallbacks instead of one generic fallback.
Examples:
- token info unavailable → price unavailable, header preserved, footer says so
- signal unavailable → signal fields become unavailable without collapsing whole card
- market rank unavailable → `/watchtoday` keeps signals if they still exist
- audit unavailable → `Audit gate: Unverified`, footer warns explicitly

## Layer 3 — Publishing Loop

### Square post templates
#### Template A — Clean board day
Smart money is active today.

[Signal name] — [n] wallets buying.
[Token] leads attention with [n] searches.

Posture: [holdings verdict].

Bibipilot · [date] · #AIBinance

#### Template B — Hype day
High attention today. Low signal quality.

[Token] trending — [n] searches, $[liq] liquidity.
No matched smart-money signal visible.

Stay selective. Dry powder > chasing hype.

Bibipilot · [date] · #AIBinance

#### Template C — Quiet board
Quiet board today.

No strong smart-money signals visible.
Attention spread thin across [n] tokens.

Best move: hold posture. Wait for the board.

Bibipilot · [date] · #AIBinance

### Posting flow
Default flow:
1. `/watchtoday`
2. generate draft
3. show for approval
4. publish only after explicit confirmation

### Auto-suggest logic
- strong board → Template A
- hype without signal → Template B
- low-action board → Template C

## Layer 4 — Competition-Specific Additions

### `/compare <symbol> <symbol>`
Side-by-side asset comparison for judges and fast decision-making.

### `/day`
Daily summary command that combines board + posture + best setup.

### `/flow <symbol>`
Deeper smart-money accumulation / distribution read.
Lower priority than `/day` for competition-week delivery.

## Recommended Order

### Competition week
1. verdict fragments lock
2. trend vocabulary
3. liquidity labels
4. `/signal` entry zone
5. `/watchtoday` signal age
6. `/watchtoday` board verdict vocabulary
7. Square post templates
8. `/day`
9. `/compare`

### After competition
1. snapshot system
2. rotation detection
3. parallel skill calls
4. per-skill error recovery
5. deeper ownership logic
6. `/audit` structured check counts
7. `/flow`
8. auto-post trigger logic
