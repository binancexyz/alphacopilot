# OpenClaw Command Templates

These are suggested runtime command patterns for the canonical command surface.

## `/brief <symbol>`
Runtime goal:
1. parse symbol
2. call live skills
3. build raw payload map
4. pass to extractor/normalizer
5. return formatted brief

Suggested logical flow:
- parse user input into `symbol`
- collect outputs from:
  - `query-token-info`
  - `crypto-market-rank`
  - `trading-signal`
  - `query-token-audit`
- build raw payload dict
- call `extract_token_context(raw_payload, symbol)` when deeper context is needed
- normalize
- build brief
- return response

### `/brief <symbol> deep`
Use the fuller asset path with:
- `query-token-info`
- `crypto-market-rank`
- `trading-signal`
- `query-token-audit`

## `/signal <token>`
Same pattern with:
- `trading-signal`
- `query-token-info`
- `query-token-audit`

## `/holdings <address>`
Same pattern with:
- `query-address-info`
- optional holding enrichment

## `/holdings`
Suggested runtime shape:
- use signed Binance account-read endpoints
- compute posture, concentration, freshness, and drift
- preserve private posture inside the unified holdings command

## `/watchtoday`
Same pattern with:
- `crypto-market-rank`
- `meme-rush`
- `trading-signal`

## `/audit <symbol>`
Suggested runtime shape:
- use `query-token-audit` as the safety anchor
- enrich with token context when available
- fold meme/lifecycle context into audit findings when relevant
