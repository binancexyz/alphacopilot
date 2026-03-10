# Live Adapter TODO

## Token context
- [ ] connect `query-token-info`
- [ ] connect `crypto-market-rank`
- [ ] connect `trading-signal`
- [ ] connect `query-token-audit`
- [ ] normalize result shape for `get_token_context()`

## Wallet context
- [ ] connect `query-address-info`
- [ ] enrich major holdings if needed
- [ ] normalize result shape for `get_wallet_context()`

## Watch today context
- [ ] connect `crypto-market-rank`
- [ ] connect `meme-rush`
- [ ] connect `trading-signal`
- [ ] normalize result shape for `get_watch_today_context()`

## Signal context
- [ ] connect `trading-signal`
- [ ] connect `query-token-info`
- [ ] connect `query-token-audit`
- [ ] normalize result shape for `get_signal_context()`

## Final polish
- [ ] add tests for normalized context
- [ ] add examples for live mode
- [ ] add error handling / fallback messaging
