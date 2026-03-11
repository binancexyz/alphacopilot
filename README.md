# Bibipilot

**Less noise. Better conviction.**

**Bibipilot** is the active product and repo name.

Bibipilot is an OpenClaw-based AI research assistant powered by Binance Skills Hub. It helps users analyze tokens, wallets, market signals, and risk in one place, then turns fragmented crypto data into a clear research brief.

## Quick Start

```bash
cd bibipilot
python3 src/main.py token BNB
python3 src/main.py brief BNB
python3 src/main.py price BNB
python3 src/main.py risk BNB
python3 src/main.py wallet 0x1234567890ab
python3 src/main.py watchtoday
python3 src/main.py watch today
python3 src/main.py signal DOGE
```

## Contest Framing

This project is designed as a **signal-and-risk research copilot** for the Binance + OpenClaw builder direction.
Instead of focusing on hype alone, it focuses on whether a signal is actually worth attention.

## Core Idea

Most crypto tools tell users what is moving.

Bibipilot goes further: it helps users understand whether a signal is actually worth attention, what the risks are, and what to watch next before conviction increases.

## Problem

Crypto research is fragmented and noisy. Users often jump between:
- token trackers
- wallet explorers
- market dashboards
- signal tools
- contract risk checkers

This creates too much noise and not enough interpretation.

## Solution

Bibipilot combines Binance Skills Hub capabilities into a signal-and-risk research workflow.

It does not force every command into one generic answer shape.
Instead, each command is designed to answer its own question well:

- `/price` -> compact market card
- `/brief` -> ultra-compact synthesis
- `/risk` -> downside-first risk card
- `/token` -> token setup + risk + watch view
- `/signal` -> setup validity and timing read
- `/wallet` -> wallet interpretation and followability
- `/watchtoday` -> market prioritization

The longer-term design direction is:

**research -> judgment -> publishing**

That means Binance Skills provide raw evidence, Bibipilot adds interpretation, and `square-post` becomes the publishing layer.

## Core Features

### 1. Token Intel
Analyze token context, liquidity, holders, signal quality, and risk.

### 2. Wallet Intel
Interpret wallet behavior, concentration, exposure, and risk posture.

### 3. Watch Today
Summarize top narratives, strongest signals, and main risk zones.

### 4. Signal Check
Explain whether a trading signal is meaningful, fragile, or worth monitoring.

### 5. Square Publishing
Convert research output into a Binance Square-ready short post and treat publishing capability as a core part of the product.

## Binance Skills Used

Primary research skills:
- `query-token-info`
- `query-address-info`
- `crypto-market-rank`
- `trading-signal`
- `query-token-audit`
- `meme-rush`

Required publishing/output skill:
- `square-post`

Deferred higher-risk execution skill:
- `spot`

## Latest Integration Direction

The latest project lesson is to treat Binance capabilities primarily as **Skills/runtime tools**, not as guessed standalone REST endpoints.

That means the preferred live path is:
- OpenClaw/runtime invokes Binance Skills
- raw skill outputs are collected
- Python extracts, normalizes, interprets, and formats

This repo already supports the repo-side normalization/brief pipeline. The remaining live work is to connect the real Binance Skills/runtime layer cleanly.

## Recommended Stack

- **OpenClaw** — agent runtime
- **Binance Skills Hub** — crypto skill layer
- **Python** — reusable logic and formatting
- **Telegram** — primary chat/demo interface
- **GitHub** — source control and long-term project home

## Helper Scripts

- `scripts/check_all.sh` — run local checks
- `scripts/demo_capture.sh` — print demo-friendly command output
- `scripts/summary.sh` — print a quick repo/project summary
- `scripts/export_examples.sh` — export current command outputs into example files
- `scripts/runtime_demo_all.sh` — run the raw-payload runtime demo flow

## API Mode

A lightweight FastAPI app is included for serving formatted briefs.

Note: the core CLI works in mock mode without optional API/live HTTP dependencies installed. The API and HTTP live mode require installing `requirements.txt`.

```bash
make api
```

## Binance Square Posting

A required Square posting flow is included.
It now supports:
- Binance Square draft/publish via `src/square_cli.py`
- scheduled posting via `src/square_diary.py`
- direct autoposting with env-based credentials
- a verified 7-slot Asia/Phnom_Penh cron schedule
- rotating morning-diary / education / market / builder / ecosystem / motivation / night-diary content slots

```bash
python3 src/square_cli.py token BNB
python3 src/square_diary.py ecosystem --dry-run
```

Endpoints:
- `/health`
- `/brief/token?symbol=BNB`
- `/brief/signal?token=DOGE`
- `/brief/wallet?address=0x1234567890ab`
- `/brief/watchtoday`

Responses include:
- `command`
- `entity`
- `mode`
- `rendered`
- optional `warning`

## Project Status

This repo is currently a **strong runnable scaffold**.

What is already here:
- command architecture for `/token`, `/brief`, `/price`, `/risk`, `/signal`, `/wallet`, `/watchtoday`, and `watch today`
- normalized data contracts
- mock/live service split
- heuristics and formatter logic
- tests and repo automation
- submission and launch docs

What still depends on runtime integration:
- real OpenClaw live command wiring
- real Binance Skills Hub tool invocation
- live payload collection from runtime outputs

What is now available for local live-mode development:
- file-based live payload loading via `BINANCE_SKILLS_BASE_URL=file:///absolute/path/to/payloads`
- HTTP adapter loading via `BINANCE_SKILLS_BASE_URL=https://...`
- runtime bridge template flows that use raw payloads when provided
- improved end-to-end `/token BNB` live matching in both bridge and extractor layers
- working live Binance Square publishing from chat and CLI
- scheduled Binance Square autoposting with a verified quality-focused 7-post/day cron engine in `src/square_diary.py`
- `make bridge-live` for starting the local bridge with `.env` loaded
- compact `/price`, `/brief`, and `/risk` flows with stable market quotes using CoinGecko-first live sourcing and fallback behavior

## Architecture

### Layer 1 — OpenClaw
- agent runtime
- command routing
- chat interaction
- tool usage

### Layer 2 — Binance Skills Hub
- token data
- wallet analysis
- market rankings
- trading signals
- token audit checks

### Layer 3 — Python Logic
- signal interpretation
- wallet behavior summaries
- risk tagging
- response formatting
- conviction summaries

### Layer 4 — Interface
- Telegram first
- web UI later if needed

## MVP Commands

- `/token <symbol>`
- `/wallet <address>`
- `/watchtoday`
- `/signal <token>`

## What Makes It Different

Bibipilot is not just another crypto assistant.

It is a **signal-and-risk copilot**.

Its goal is not to maximize noise. Its goal is to improve conviction.

## Key Docs

- `docs/submission.md` — full contest submission draft
- `docs/submission-short.md` — short submission version
- `docs/demo-script.md` — demo flow
- `docs/token-live-design.md` — first real live integration target
- `docs/live-command-mapping.md` — live command architecture
- `docs/normalized-data-contracts.md` — normalized context shapes
- `docs/live-integration-checklist.md` — final engineering checklist
- `docs/github-metadata.md` — repo naming and metadata
- `docs/release-checklist.md` — launch checklist
- `docs/maintainer-summary.md` — shortest return-to-project summary
- `docs/commands-overview.md` — command intent at a glance
- `docs/heuristics-overview.md` — current heuristic layer summary
- `docs/developer-flow.md` — practical day-to-day workflow
- `docs/INDEX.md` — docs directory index
- `docs/faq.md` — short project FAQ
- `docs/local-dev.md` — local development quick guide
- `docs/review-checklist.md` — change review checklist
- `docs/release-prep.md` — quick release-prep path
- `docs/final-hand-off.md` — best resume/handoff notes
- `SECURITY-CHECKLIST.md` — project security checklist
- `docs/security-principles.md` — core security approach

## Judge-Friendly Pitch

Bibipilot helps users understand not just what is moving, but whether it is actually worth attention.
