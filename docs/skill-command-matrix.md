# Skill-to-Command Matrix

This document captures the current best design direction for Bibipilot.

The key rule is simple:

**Every output section should map to a deliberate Binance Skill input.**

Bibipilot is strongest when it behaves like a:

**research -> judgment -> publishing** pipeline.

---

## Core skills

### Research core
- `query-token-info`
- `query-token-audit`
- `query-address-info`
- `trading-signal`
- `crypto-market-rank`
- `meme-rush`

### Publishing core
- `square-post`

### Deferred execution
- `spot`

---

## Master matrix

| Skill | /token | /signal | /wallet | /watchtoday | /meme | /audit |
|---|---|---|---|---|---|---|
| `query-token-info` | Primary | Support | - | Support | Primary | - |
| `query-token-audit` | Hard gate | Hard gate | - | - | Gate | Primary |
| `trading-signal` | Signal | Primary | - | Confirm | Support | - |
| `query-address-info` | - | - | Primary | - | - | - |
| `crypto-market-rank` | Rank context | Confirm | PnL rank | Primary | Meme rank | - |
| `meme-rush` | If meme | - | - | Primary | Primary | - |
| `square-post` | Publish | Publish | - | Publish | Publish | - |

---

## Hard rule: audit gate

`query-token-audit` should be treated as a gate, not a decorative note.

### Block state
If audit shows critical danger such as:
- honeypot
- scam flag
- critical fail

Bibipilot should:
- suppress bullish signal framing
- suppress "worth watching" tone
- show a red blocked state instead

### Warn state
If audit shows medium-risk issues such as:
- mint enabled
- freeze enabled
- owner control
- high tax
- partial / incomplete audit support

Bibipilot may continue, but must frame the asset as higher-risk and lower-conviction.

### Allow state
If audit is clean enough, the rest of the command can render normally.

---

## Command design

## `/token`

### Purpose
Answer:

**Is this token actually worth attention right now?**

### Primary inputs
- `query-token-info`
- `query-token-audit`
- `trading-signal`
- optional `crypto-market-rank`

### Best output shape
- Header
- Market Read
- Audit Gate
- Smart Signal
- Smart Money Context
- Watch
- Tags

### Important fields to expose
- price
- market cap
- volume
- holders
- liquidity
- `smartMoneyCount`
- `alertPrice`
- `highestPrice`
- `exitRate`
- `isAlpha`
- `launchPlatform`
- inflow rank
- social rank

---

## `/signal`

### Purpose
Answer:

**Should I trust this setup now, or is it already late / weak / blocked?**

### Primary inputs
- `trading-signal`
- `query-token-audit`
- optional `crypto-market-rank`

### Best output shape
- Audit Gate
- Setup
- Strength
- Confluence
- Exit Watch
- Risk Level

### Important judgment logic
- convert `timeFrame` into signal age
- label freshness as `FRESH`, `AGING`, or `STALE`
- use `exitRate` to decide whether smart money is still in or already out

### Important principle
If audit blocks the token, do not show a bullish signal summary.

---

## `/wallet`

### Purpose
Answer:

**Is this wallet worth tracking?**

### Primary inputs
- `query-address-info`
- `crypto-market-rank` Address PnL Rank

### Best output shape
- Portfolio
- Top Holdings
- Style Read
- PnL Rank
- Verdict
- Watch Tokens
- Flags

### Desired judgment layer
Bibipilot should not stop at listing positions.
It should give a usable verdict such as:
- `✅ Track`
- `⚠️ Unknown`
- `❌ Don't follow`

---

## `/watchtoday`

### Purpose
Answer:

**What matters most in the market today?**

### Primary inputs
- `crypto-market-rank`
- `meme-rush`
- optional `trading-signal`
- optional `query-token-info`

### Best output shape
- Trending Now
- Smart Money Flow
- Social Hype
- Meme Watch
- Narrative
- Today's Top 3
- Market Risk

### Design rule
Do not blend all feeds into one vague summary. Keep the feeds named and visible.

---

## Proposed new commands

## `/meme`

### Purpose
Fast scan for meme plays.

### Inputs
- `meme-rush`
- `query-token-audit`
- `query-token-info`
- optional `trading-signal`

### Best output shape
- Lifecycle Stage
- Audit Gate
- Token Read
- Smart Money Context
- Watch

---

## `/audit`

### Purpose
Pure security report.

### Inputs
- `query-token-audit`

### Best output shape
- Overall Status
- Honeypot
- Scam
- Mint
- Freeze
- Owner Control
- Tax
- Verification
- Disclaimer

This command should avoid market narrative and focus only on security posture.

---

## Square publishing layer

Rich research output and good Binance Square posts are not the same thing.

Bibipilot should use a compression layer:

1. fetch skills
2. normalize
3. judge
4. render command output
5. compress for Square
6. publish via `square-post`

This makes public output shorter without weakening internal analysis quality.

---

## Architecture upgrades

### 1. Parallel skill execution
Commands such as `/token` and `/meme` should fetch multiple skills in parallel when possible.

### 2. Audit short-circuit
If audit fails critically, skip the bullish path and render blocked output immediately.

### 3. Signal freshness labels
Use signal age from `timeFrame` to label setups as:
- `FRESH`
- `AGING`
- `STALE`

### 4. Exit-rate interpretation
If `exitRate` is high, Bibipilot should state clearly that the setup may be late.

---

## Judge-facing summary

The clearest product story is:

**Bibipilot uses Binance Skills to research assets, apply judgment, and publish only what is worth attention.**

That means it is not just an AI formatter.
It is a Binance-native decision pipeline.
