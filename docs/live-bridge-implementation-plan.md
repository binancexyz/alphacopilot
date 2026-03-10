# Live Bridge Implementation Plan

## Goal
Get Bibipilot onto real Binance skill data with the least architectural mess.

## Best solution
Build a small Binance Skills bridge and point Bibipilot at it with:

```env
APP_MODE=live
BINANCE_SKILLS_BASE_URL=https://your-bridge.example.com/runtime
```

## Why this is best
- keeps live skill invocation separate from interpretation
- matches the Binance Skills model
- keeps Bibipilot reusable
- simplifies testing/debugging
- lets Square posting remain a separate product/output capability

## Phase 1 — Token bridge
Implement one bridge endpoint that supports:
- `command=token`
- `entity=<symbol>`

Bridge must call:
- `query-token-info`
- `crypto-market-rank`
- `trading-signal`
- `query-token-audit`

Return a raw payload bundle.

## Phase 2 — Signal bridge
Add:
- `command=signal`

Bridge must call:
- `trading-signal`
- `query-token-info`
- `query-token-audit`

## Phase 3 — Watchtoday bridge
Add:
- `command=watchtoday`

Bridge must call:
- `crypto-market-rank`
- `meme-rush`
- `trading-signal`

## Phase 4 — Wallet bridge
Add:
- `command=wallet`
- `entity=<address>`

Bridge must call:
- `query-address-info`
- optional token enrichment later

## Phase 5 — Deployment hardening
- auth or private network
- structured logs without secrets
- rate limiting
- timeouts/retries
- health endpoint
- partial-failure reporting

## Bibipilot-side checklist
Already largely done in repo:
- live adapter path
- raw extractors
- normalizers
- brief builders
- Square post scaffold
- bridge scaffold API (`src/bridge_api.py`)

Remaining Bibipilot-side improvements:
- richer analyzer language tuned to real skill semantics
- better partial failure wording
- more real-payload fixture tests

## Recommended bridge stack
Use the smallest practical stack available in your environment.
Good options:
- lightweight FastAPI/Node service
- OpenClaw-native runtime wrapper if reliable and accessible

## Success condition
A real live token request works end-to-end:
1. bridge invokes Binance Skills
2. Bibipilot receives raw payload bundle
3. Bibipilot produces brief
4. optional Square post can be generated/published from real brief
