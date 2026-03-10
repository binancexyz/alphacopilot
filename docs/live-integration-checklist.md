# Live Integration Checklist

This is the final practical checklist for turning the scaffold into a live OpenClaw-powered assistant.

## Phase 1 — `/token`
- [ ] parse `/token <symbol>` in the runtime flow
- [ ] call `query-token-info`
- [ ] call `crypto-market-rank`
- [ ] call `trading-signal`
- [ ] call `query-token-audit`
- [ ] collect raw outputs into one payload
- [ ] pass payload through `extract_token_context(...)`
- [ ] normalize with `normalize_token_context(...)`
- [ ] build final brief with `build_token_brief(...)`
- [ ] return formatted output

## Phase 2 — `/signal`
- [ ] parse `/signal <token>`
- [ ] call `trading-signal`
- [ ] call `query-token-info`
- [ ] call `query-token-audit`
- [ ] extract with `extract_signal_context(...)`
- [ ] normalize with `normalize_signal_context(...)`
- [ ] build final brief with `build_signal_brief(...)`

## Phase 3 — `/wallet`
- [ ] parse `/wallet <address>`
- [ ] call `query-address-info`
- [ ] optionally enrich top holdings
- [ ] extract wallet payload
- [ ] normalize with `normalize_wallet_context(...)`
- [ ] build final brief with `build_wallet_brief(...)`

## Phase 4 — `/watchtoday`
- [ ] call `crypto-market-rank`
- [ ] call `meme-rush`
- [ ] call `trading-signal`
- [ ] extract watch payload
- [ ] normalize with `normalize_watch_today_context(...)`
- [ ] build final brief with `build_watchtoday_brief(...)`

## Phase 5 — polish
- [ ] add better fallback messages
- [ ] add beginner/pro mode
- [ ] refine heuristics from real data patterns
- [ ] record demo video with live or semi-live flow
