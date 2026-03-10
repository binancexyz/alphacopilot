# OpenClaw Command Templates

These are suggested runtime command patterns for the first live integration phase.

## `/token <symbol>`
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
- call `extract_token_context(raw_payload, symbol)`
- normalize
- build brief
- return response

## `/signal <token>`
Same pattern with:
- `trading-signal`
- `query-token-info`
- `query-token-audit`

## `/wallet <address>`
Same pattern with:
- `query-address-info`
- optional holding enrichment

## `/watchtoday`
Same pattern with:
- `crypto-market-rank`
- `meme-rush`
- `trading-signal`
