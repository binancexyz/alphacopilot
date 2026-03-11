# Submission Draft

## Project Name
**Bibipilot**

**Short Name:** Bibipilot

## Tagline
**Bibipilot checks what’s moving, filters what’s dangerous, and publishes what’s worth attention.**

## Short Description
Bibipilot is a Binance-native research copilot that turns Binance Skills outputs into clearer judgment and publishable Binance Square content.

## Problem
Crypto research is fragmented, noisy, and too often missing a judgment layer.

Users can find token dashboards, wallet activity, trending sectors, smart-money movement, and risk tools separately, but that still leaves the hardest questions unanswered:
- what is actually worth attention?
- what is dangerous?
- what is early versus late?
- what is worth publishing for other users?

That gap between raw attention and usable conviction is the real problem.

## Solution
Bibipilot closes that gap by turning Binance Skills outputs into a full workflow:

### 1. Research
It pulls token, signal, wallet, audit, market-rank, and meme-style context from Binance Skills.

### 2. Judgment
It converts that raw context into clearer decisions such as:
- audit gate states
- follow-or-ignore wallet verdicts
- daily market prioritization
- risk-aware token and signal interpretation
- fast meme-style scan behavior

### 3. Publishing
It formats outputs for chat and Binance Square, then publishes live text posts directly.

So Bibipilot is not just an AI that summarizes crypto.
It is a **research -> judgment -> publishing** product.

## Current Command Surface
- `/price` — compact market card
- `/brief` — fast synthesis
- `/risk` — downside-first risk read
- `/audit` — security-first audit card
- `/token` — token setup and conviction read
- `/signal` — timing and setup validation
- `/wallet` — wallet interpretation with follow verdict
- `/watchtoday` — daily market board with live lanes
- `/meme` — first-pass meme scan

## Skills Used
### Research core
- `query-token-info`
- `query-token-audit`
- `query-address-info`
- `trading-signal`
- `crypto-market-rank`
- `meme-rush`

### Publishing core
- `square-post`

### Deferred
- `spot`

## What Makes Bibipilot Stand Out
### 1. It has a real judgment layer
Bibipilot does not stop at surfacing movement.
It tries to answer what deserves conviction, caution, or rejection.

### 2. It is Binance-native
Its architecture and product story are grounded in Binance Skills, Binance Spot read-only market data, and Binance Square — not generic crypto prompts.

### 3. It closes the loop
Most entries stop at analysis.
Bibipilot continues into live publishing.
That makes it feel like a real product, not just a demo.

### 4. It is easy to understand live
The command surface is clear, chat-friendly, and demoable in a few minutes.

## Live Proof Points
- live Binance Square posting works
- a scheduled premium 1-post/day Binance Square engine is active
- Binance Spot read-only grounding now strengthens `/price`, `/brief`, and `/watchtoday`
- `/watchtoday` now renders live market lanes with an Exchange Board anchor
- `/audit` is a first-class command
- `/wallet` includes explicit follow verdicts and stronger behavior judgment
- `/meme` exists as a first-pass command
- live runtime health diagnostics now exist via `/health`

## Why It Matters
People do not need more crypto noise.
They need a system that can:
- check what matters
- filter what is dangerous
- rank attention
- and publish useful output fast

That is the role Bibipilot is designed to play.

## Closing Line
Bibipilot turns noisy crypto signals into clearer judgment, then turns that judgment into publishable Binance Square output.
