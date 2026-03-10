# Architecture

## Goal
Build a contest-friendly OpenClaw assistant that is also easy to evolve later.

## Design Principle
Keep the **runtime**, **domain logic**, and **output formatting** separate.

That lets the project:
- use OpenClaw now for challenge alignment
- keep Python logic reusable later
- migrate to a different runtime if needed
- align cleanly with Binance Skills as runtime-invoked capabilities rather than overfitting to guessed direct REST endpoints

## Layers

### 1. Runtime Layer
Current choice:
- OpenClaw

Responsibilities:
- agent runtime
- chat orchestration
- tool routing
- interaction flow

### 2. Crypto Capability Layer
Current choice:
- Binance Skills Hub

Responsibilities:
- token intelligence via `query-token-info`
- wallet/address intelligence via `query-address-info`
- market rankings via `crypto-market-rank`
- signal data via `trading-signal`
- token audit checks via `query-token-audit`
- meme trend context via `meme-rush`
- required publishing via `square-post`
- deferred execution via `spot`

### 3. Domain Logic Layer
Current choice:
- Python modules in `src/analyzers/`

Responsibilities:
- synthesize tool outputs
- interpret signal quality
- summarize wallet behavior
- attach risk tags
- produce conviction summaries

### 4. Output Layer
Current choice:
- Python formatters in `src/formatters/`

Responsibilities:
- convert analysis into consistent sections
- keep replies concise and readable
- enforce product voice

### 5. Interface Layer
Current choice:
- Telegram via OpenClaw

Future options:
- web UI
- FastAPI service
- other messaging surfaces

## MVP Command Map

### `/token <symbol>`
Input -> token info + market rank + trading signal + token audit -> structured brief

### `/wallet <address>`
Input -> address info + enrichment -> behavior summary + risk posture

### `/watchtoday`
Input -> market rank + meme rush + trading signals -> top narratives + risk zones

### `/signal <token>`
Input -> trading signal + token context + audit -> signal quality + confirmation conditions

## Migration Strategy
To make runtime migration easy later:
- keep prompts and agent files under `agent/`
- keep reusable logic under `src/`
- avoid putting core business logic only in prompt text
- treat OpenClaw as the runtime shell, not the entire product
