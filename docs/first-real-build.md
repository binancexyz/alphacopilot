# First Real Build Plan

## Highest-value next engineering target
Implement `/token` with a real live adapter path.

## Build steps
1. Keep OpenClaw as the runtime shell
2. Collect raw outputs from:
   - query-token-info
   - crypto-market-rank
   - trading-signal
   - query-token-audit
3. Feed those raw outputs into `extract_token_context(...)`
4. Normalize into `TokenContext`
5. Use `analyze_token(...)` to build final brief
6. Return formatted response

## Why this is the right first step
- strongest demo path
- most understandable result
- best bridge from concept to real product
- easiest to reuse later in `/signal`

## After `/token`
Next best order:
1. `/signal`
2. `/wallet`
3. `/watchtoday`
