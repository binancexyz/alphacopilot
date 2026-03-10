# OpenClaw Runtime Integration

This document describes the intended live integration path using OpenClaw as the runtime shell.

## Runtime role
OpenClaw should:
- receive the user command
- route it to the right live-skill sequence
- gather raw tool outputs
- pass a normalized payload into the Python interpretation layer
- send the final formatted brief back to the user

## Integration principle
Do not put all business logic into prompt text.
Use prompt/rules for behavior, but keep extraction, normalization, and heuristics in Python.

## First command to wire
Start with `/token <symbol>`.

## Why
- strongest demo value
- clearest multi-skill path
- easiest to reuse later for `/signal`

## Runtime pipeline
1. parse user input
2. call live skills
3. collect raw outputs into a dict
4. call extractor
5. call normalizer
6. call analyzer/brief builder
7. call formatter
8. send final response

## Live-skill sequence by command
### `/token`
- `query-token-info`
- `crypto-market-rank`
- `trading-signal`
- `query-token-audit`

### `/signal`
- `trading-signal`
- `query-token-info`
- `query-token-audit`

### `/wallet`
- `query-address-info`
- optional enrichment

### `/watchtoday`
- `crypto-market-rank`
- `meme-rush`
- `trading-signal`
