# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What is Bibipilot

A Binance-native signal-and-risk research copilot. It filters crypto signals, interprets risk, and publishes to Binance Square. The goal is to answer "what matters about this asset right now?" with calm, credible judgment — never hype.

## Commands

```bash
make check          # Compile-check all .py files (py_compile)
make test           # Run full test suite (tests/run_tests.py)
make api            # Start REST API on :8000
make bridge-api     # Start OpenClaw bridge on :8010
make token          # CLI: token analysis for BNB
make signal         # CLI: signal analysis for DOGE
make wallet         # CLI: wallet analysis
make watchtoday     # CLI: daily market board
```

**CLI usage:** `python3 src/main.py <command> [args]`
- `brief <symbol>` — fast default read; add `deep` for full token judgment
- `signal <symbol>` — timing quality, setup fragility
- `holdings [address]` — portfolio posture (no arg) or wallet behavior (0x address)
- `watchtoday` — daily market board
- `audit <symbol>` — security/safety read with meme lens

**Before any PR:** `make check && make test`

## Architecture

**Request flow:** Input → Parsing/Validation (`utils/`) → Data Collection (`services/`) → Normalization → Analysis (`analyzers/`) → Formatting (`formatters/`) → Output

**Key architectural decisions:**

- **Service factory pattern** — `services/factory.py` returns `MockMarketDataService` (default, local dev) or `LiveMarketDataService` based on `APP_MODE` env var. All services implement the `MarketDataService` protocol (`services/interfaces.py`).
- **Mock by default** — `APP_MODE=mock` is the default. No API keys needed for local development.
- **Three runtime surfaces** — CLI (`main.py`), REST API (`api.py` on :8000), OpenClaw bridge (`bridge_api.py` on :8010). All share the same analyzers/services.
- **Each command has its own analyzer and output shape** — don't force commands into a generic template.
- **Normalizer layer** — `services/normalizers.py` and `services/live_extractors.py` transform raw Binance Skills payloads into normalized dicts before analyzers consume them.

**Source layout:**
- `src/analyzers/` — judgment logic per command (brief, token, signal, audit, wallet, market_watch, portfolio)
- `src/services/` — data loading, normalization, integrations, API guard
- `src/formatters/` — rich terminal output rendering
- `src/models/` — data schemas (AnalysisBrief, RiskTag, etc.)
- `src/utils/` — parsing, validation helpers

**Tests** use direct function calls (no pytest framework). The runner at `tests/run_tests.py` imports and calls each test function sequentially. API tests are conditionally skipped if FastAPI test deps are missing.

## Configuration

Environment loaded from `.env.local` (preferred) or `.env` via `src/config.py`. Key variables:
- `APP_MODE` — `mock` (default) or `live`
- `BINANCE_SKILLS_BASE_URL`, `BINANCE_API_KEY`, `BINANCE_API_SECRET` — required for live mode
- `API_AUTH_ENABLED`, `API_AUTH_KEY` — HMAC auth for REST API
- `BRIDGE_LIVE_ENABLED` — enables live bridge mode

## Product voice

- Lead with the answer, prefer interpretation over raw data
- Keep risk visible — never hide it
- Calm, credible language — no hype, no certainty claims
- Flag incomplete or weak evidence clearly
- Avoid: "guaranteed", "safe bet", "will pump". Prefer: "worth monitoring", "elevated risk", "requires confirmation"
