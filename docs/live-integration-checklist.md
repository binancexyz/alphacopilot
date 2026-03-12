# Live Integration Checklist

This is the final practical checklist for turning the scaffold into a live OpenClaw-powered assistant.

## Phase 1 — `/brief deep`
- [ ] parse `/brief <symbol> deep` in the runtime flow
- [ ] call `query-token-info`
- [ ] call `crypto-market-rank`
- [ ] call `trading-signal`
- [ ] call `query-token-audit`
- [ ] collect raw outputs into one payload
- [x] pass payload through `extract_token_context(...)`
- [x] normalize with `normalize_token_context(...)`
- [x] build final brief with `build_token_brief(...)`
- [x] return formatted output once a raw payload is available

## Phase 2 — `/signal`
- [ ] parse `/signal <token>`
- [ ] call `trading-signal`
- [ ] call `query-token-info`
- [ ] call `query-token-audit`
- [x] extract with `extract_signal_context(...)`
- [x] normalize with `normalize_signal_context(...)`
- [x] build final brief with `build_signal_brief(...)`

## Phase 3 — `/holdings <address>`
- [ ] parse `/holdings <address>`
- [ ] call `query-address-info`
- [ ] optionally enrich top holdings
- [x] extract wallet payload
- [x] normalize with `normalize_wallet_context(...)`
- [x] build final brief with `build_wallet_brief(...)`

## Phase 4 — `/watchtoday`
- [ ] call `crypto-market-rank`
- [ ] call `meme-rush`
- [ ] call `trading-signal`
- [x] extract watch payload
- [x] normalize with `normalize_watch_today_context(...)`
- [x] build final brief with `build_watchtoday_brief(...)`

## Phase 5 — polish
- [ ] add better fallback messages
- [ ] add beginner/pro mode
- [ ] refine heuristics from real data patterns
- [ ] record demo video with live or semi-live flow
