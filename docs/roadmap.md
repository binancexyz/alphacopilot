# Roadmap

## Phase 1 — Research MVP (complete)
- [x] Finalize product framing
- [x] Build `/token`
- [x] Build `/wallet`
- [x] Build `/watchtoday`
- [x] Build `/signal`
- [x] Build `/price`
- [x] Build `/brief`
- [x] Build `/risk`
- [x] Build `/audit`
- [x] Build `/meme`
- [x] Build `careers` ecosystem intelligence
- [x] Standardize output format (AnalysisBrief with rich formatting)
- [x] Prepare demo and submission
- [x] Build FastAPI REST API (v0.2.1) with security middleware
- [x] Build OpenClaw live bridge API (v0.2.0)
- [x] Build Binance Square publishing with draft/publish support
- [x] Build scheduled premium 1-post/day engine with 7 diary series
- [x] Add API security hardening (auth, rate limiting, SSRF, path traversal, headers)
- [x] Keep scope research-first and human-supervised

## Phase 2 — Live Binance Skills Alignment (in progress)
- [x] Wire real `query-token-info`
- [x] Wire real `query-token-audit`
- [x] Wire real `trading-signal`
- [x] Wire real `crypto-market-rank`
- [x] Wire real `meme-rush`
- [ ] Wire real `query-address-info` (wallet live context still thinner)
- [x] Validate payload/field assumptions against real Binance Skills outputs
- [x] Make `square-post` a working publishing/output path
- [ ] Strengthen wallet and meme live bridge context
- [ ] Final production payload validation

## Phase 3 — Product Polish
- [ ] Add beginner/pro mode
- [ ] Add shareable summary mode
- [ ] Improve risk tags and conviction labels
- [ ] Add better examples and screenshots
- [ ] Improve fallback messaging from partial live skill failures

## Phase 4 — Long-Term Productization
- [ ] Add watchlists and saved preferences
- [ ] Add persistent reports/history
- [ ] Add optional web UI
- [ ] Add optional alerts and scheduled digests
- [ ] Consider `spot` only as a later, explicitly gated, higher-risk execution capability

## Guiding Rule
Build like a product, demo like a prototype, and keep execution features behind stricter safety gates than research features.
