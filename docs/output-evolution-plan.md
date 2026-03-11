# Output Evolution Plan

This document turns the current improvement direction into a practical build order.

## Goal

Move Bibipilot from a good formatter into a stronger research-and-judgment product.

---

## Phase 1 — trust and safety

### 1. Audit hard gate
Apply first to:
- `/token`
- `/signal`
- later `/meme`

If audit returns critical danger, suppress bullish signal language and render a blocked state.

### 2. Signal freshness
Parse `timeFrame` into age and label setups:
- `FRESH`
- `AGING`
- `STALE`

Use tighter stale thresholds for meme tokens.

### 3. Exit-rate judgment
Interpret `exitRate` as early / mixed / late participation rather than leaving it as a hidden raw field.

---

## Phase 2 — command-specific intelligence upgrades

### `/token`
Add:
- smart money context
- audit gate block
- rank confluence
- `smartMoneyCount`
- `isAlpha`
- `launchPlatform`

### `/signal`
Add:
- signal age
- entry vs now
- exit-rate read
- confluence with market-rank data
- stronger tactical tone

### `/wallet`
Add:
- Address PnL Rank check
- wallet-follow verdict
- narrative bias
- chain bias
- stronger flags

### `/watchtoday`
Split the output into named lanes:
- Trending Now
- Smart Money Flow
- Social Hype
- Meme Watch
- Narrative
- Today's Top 3
- Market Risk

---

## Phase 3 — new commands

### `/audit`
Add a pure security command based only on `query-token-audit`.

### `/meme`
Add a fast meme scan command powered by:
- `meme-rush`
- `query-token-audit`
- `query-token-info`
- optional `trading-signal`

---

## Phase 4 — publishing compression

Add a compression layer between internal brief rendering and Binance Square posting.

Target:
- strong public posts
- <= 1000 characters
- signal-preserving but shorter than internal analysis

---

## Phase 5 — performance and architecture

### Parallelize skill fetches
Especially for:
- `/token`
- `/meme`

### Add short-circuit paths
Stop early when a blocked audit result makes the rest of the pipeline irrelevant.

---

## Recommended execution order

1. Audit hard gate on `/token` and `/signal`
2. Signal freshness and exit-rate labeling
3. `/watchtoday` named-feed redesign
4. `/audit`
5. `/meme`
6. Square compression templates
7. Parallel skill execution

---

## Product principle

Each command should have its own output shape.

Do not force all commands into one shared template.

The right structure is the one that best answers the command's actual question.
