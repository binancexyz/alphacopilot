# Integration Plan

## Current State
The project currently ships with a working **mock scaffold** that demonstrates:
- command structure
- analysis flow
- formatting
- project framing

It does **not** yet fetch live Binance skill data.

## Integration Goal
Replace mock analyzers with a service layer that can consume real outputs from Binance Skills Hub and/or OpenClaw tool flows.

## Recommended Integration Strategy

### Phase 1 — Stable internal interface
Create service methods for:
- token context
- wallet context
- market watch context
- signal context

These methods should return normalized Python dictionaries or dataclasses.

### Phase 2 — Mock + Live adapters
Support two modes:
- `mock` for local demo and development
- `live` for real Binance/OpenClaw-backed calls

### Phase 3 — Runtime integration
Use OpenClaw as the runtime shell and route user requests into the Python logic layer.

## Suggested Service Interface

### Token
`get_token_context(symbol: str) -> dict`

Should eventually combine:
- query-token-info
- crypto-market-rank
- trading-signal
- query-token-audit

### Wallet
`get_wallet_context(address: str) -> dict`

Should eventually combine:
- query-address-info
- optional token enrichment
- optional token audit checks

### Watch Today
`get_watch_today_context() -> dict`

Should eventually combine:
- crypto-market-rank
- meme-rush
- trading-signal

### Signal
`get_signal_context(token: str) -> dict`

Should eventually combine:
- trading-signal
- query-token-info
- query-token-audit

## Runtime Direction

### Near term
- OpenClaw runtime
- Python logic modules
- Telegram interface

### Longer term
- Optional FastAPI wrapper
- Optional web UI
- Optional watchlists / persistence

## Guiding Rule
Keep domain logic independent from runtime-specific orchestration.
That makes future migration easier while preserving challenge alignment now.
