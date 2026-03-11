# Architecture

## Goal
Build a production-ready research copilot that is easy to extend, secure by default, and cleanly separated across runtime, logic, and output layers.

## Design Principle
Keep the **runtime**, **domain logic**, and **output formatting** separate.

This lets the project:
- use OpenClaw now for challenge alignment
- serve a FastAPI REST API for programmatic access
- keep Python logic reusable across runtimes
- migrate to a different runtime if needed
- align cleanly with Binance Skills as runtime-invoked capabilities

## Layers

### 1. Runtime Layer
Current implementations:
- **OpenClaw** — agent runtime, chat orchestration, tool routing
- **FastAPI REST API** (v0.2.1) — programmatic access to all research briefs
- **Live bridge API** (v0.2.0) — OpenClaw runtime integration

### 2. Crypto Capability Layer
Current choice:
- **Binance Skills Hub** (primary)
- **Binance Spot API** (supporting, read-only)

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
- Python modules in `src/analyzers/` (14 modules)

Responsibilities:
- synthesize tool outputs
- interpret signal quality and conviction levels
- summarize wallet behavior
- attach risk tags and severity
- produce conviction summaries
- build command-specific AnalysisBrief objects

### 4. Output Layer
Current choice:
- Python formatters in `src/formatters/`

Responsibilities:
- convert analysis into consistent sections
- keep replies concise and readable
- enforce product voice
- render rich terminal output

### 5. Interface Layer
Current implementations:
- **CLI** — `src/main.py` with 10 research commands
- **FastAPI** — `src/api.py` with 8 REST endpoints
- **Bridge** — `src/bridge_api.py` for OpenClaw integration
- **Square CLI** — `src/square_cli.py` for publishing
- **Diary engine** — `src/square_diary.py` for scheduled posting

Future options:
- web UI
- other messaging surfaces

## Security Layer
- API key authentication (HMAC timing-safe via `hmac.compare_digest`)
- Rate limiting (configurable requests per window)
- SSRF protection (`follow_redirects=False`, URL scheme validation)
- Path traversal prevention (`Path.is_relative_to`)
- Security headers on all responses
- Non-root container execution

## Service Architecture
- **Service factory** (`src/services/factory.py`) — selects mock or live service based on `APP_MODE`
- **Mock service** (`src/services/mock_service.py`) — hardcoded payloads for offline development
- **Live service** (`src/services/live_service.py`) — real Binance Skills adapter with caching
- **Normalizers** (`src/services/normalizers.py`) — standardize payload structure
- **Live extractors** (`src/services/live_extractors.py`) — extract data from bridge responses

## Command Map

### `/price <symbol>`
Input → Binance Spot read-only data → compact market card

### `/brief <symbol>`
Input → token info + signal + market context + Spot → fast market synthesis

### `/token <symbol>`
Input → token info + market rank + trading signal + token audit + Spot → structured brief with conviction

### `/signal <token>`
Input → trading signal + token context + audit + Spot → signal quality + confirmation conditions

### `/wallet <address>`
Input → address info + optional token enrichment + optional trader context → behavior summary + risk posture

### `/risk <symbol>`
Input → token info + audit + signal + market → downside risk assessment

### `/audit <symbol>`
Input → token audit + token info → security audit card

### `/watchtoday`
Input → market rank + meme rush + trading signals + Spot → top narratives + smart-money context + risk zones

### `/meme <symbol>`
Input → meme rush + token info → lifecycle status + holder risk + trend assessment

### `careers`
Input → Binance Careers API → ecosystem hiring pulse

## Migration Strategy
To make runtime migration easy:
- keep prompts and agent files under `agent/`
- keep reusable logic under `src/`
- avoid putting core business logic only in prompt text
- treat OpenClaw as one runtime shell, not the entire product
- FastAPI already provides a runtime-independent API surface
