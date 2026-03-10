# Roadmap

## Phase 1 — Contest MVP
- Finalize product framing
- Build `/token`
- Build `/wallet`
- Build `/watchtoday`
- Build `/signal`
- Standardize output format
- Prepare demo and submission
- Keep scope research-first and human-supervised while making Square publishing part of the core output path

## Phase 2 — Live Binance Skills Alignment
- Wire real `query-token-info`
- Wire real `query-address-info`
- Wire real `crypto-market-rank`
- Wire real `trading-signal`
- Wire real `query-token-audit`
- Wire real `meme-rush`
- Validate payload/field assumptions against real Binance Skills outputs
- Make `square-post` a must-have publishing/output path after spec/runtime confirmation

## Phase 3 — Product Polish
- Add beginner/pro mode
- Add shareable summary mode
- Improve risk tags and conviction labels
- Add better examples and screenshots
- Improve fallback messaging from partial live skill failures

## Phase 4 — Long-Term Productization
- Add FastAPI service layer
- Add watchlists and saved preferences
- Add persistent reports/history
- Add optional web UI
- Add optional alerts and scheduled digests
- Consider `spot` only as a later, explicitly gated, higher-risk execution capability

## Guiding Rule
Build like a product, demo like a prototype, and keep execution features behind stricter safety gates than research features.
