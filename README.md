# AlphaCopilot

**Less noise. Better conviction.**

**AlphaCopilot** is the short name for **Binance Alpha Copilot**.

Binance Alpha Copilot is an OpenClaw-based AI research assistant powered by Binance Skills Hub. It helps users analyze tokens, wallets, market signals, and risk in one place, then turns fragmented crypto data into a clear research brief.

## Quick Start

```bash
cd binance-alpha-copilot
python3 src/main.py token BNB
python3 src/main.py wallet 0x1234567890ab
python3 src/main.py watchtoday
python3 src/main.py signal DOGE
```

## Contest Framing

This project is designed as a **signal-and-risk research copilot** for the Binance + OpenClaw builder direction.
Instead of focusing on hype alone, it focuses on whether a signal is actually worth attention.

## Core Idea

Most crypto tools tell users what is moving.

Binance Alpha Copilot goes further: it helps users understand whether a signal is actually worth attention, what the risks are, and what to watch next before conviction increases.

## Problem

Crypto research is fragmented and noisy. Users often jump between:
- token trackers
- wallet explorers
- market dashboards
- signal tools
- contract risk checkers

This creates too much noise and not enough interpretation.

## Solution

Binance Alpha Copilot combines Binance Skills Hub capabilities into a signal-and-risk research workflow.

It turns raw tool outputs into a concise structure:
- **Quick Verdict**
- **Signal Quality**
- **Top Risks**
- **Why It Matters**
- **What To Watch Next**

Optional:
- **Risk Tags**
- **Conviction Level**
- **Beginner Note**

## Core Features

### 1. Token Intel
Analyze token context, liquidity, holders, signal quality, and risk.

### 2. Wallet Intel
Interpret wallet behavior, concentration, exposure, and risk posture.

### 3. Watch Today
Summarize top narratives, strongest signals, and main risk zones.

### 4. Signal Check
Explain whether a trading signal is meaningful, fragile, or worth monitoring.

### 5. Optional Shareable Summary
Convert research output into a short social-ready market summary.

## Binance Skills Used

- `query-token-info`
- `query-address-info`
- `crypto-market-rank`
- `trading-signal`
- `query-token-audit`
- `meme-rush`
- optional: `square-post`
- optional: `spot`

## Recommended Stack

- **OpenClaw** — agent runtime
- **Binance Skills Hub** — crypto skill layer
- **Python** — reusable logic and formatting
- **Telegram** — primary chat/demo interface
- **GitHub** — source control and long-term project home

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

Binance Alpha Copilot is not just another crypto assistant.

It is a **signal-and-risk copilot**.

Its goal is not to maximize noise. Its goal is to improve conviction.

## Key Docs

- `docs/submission.md` — full contest submission draft
- `docs/submission-short.md` — short submission version
- `docs/demo-script.md` — demo flow
- `docs/token-live-design.md` — first real live integration target
- `docs/live-command-mapping.md` — live command architecture
- `docs/normalized-data-contracts.md` — normalized context shapes
- `docs/github-metadata.md` — repo naming and metadata
- `docs/release-checklist.md` — launch checklist

## Judge-Friendly Pitch

Binance Alpha Copilot helps users understand not just what is moving, but whether it is actually worth attention.
