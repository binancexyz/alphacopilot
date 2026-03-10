# Live Adapter TODO

## Repo-side adapter status
- [x] normalize result shape for `get_token_context()`
- [x] normalize result shape for `get_wallet_context()`
- [x] normalize result shape for `get_watch_today_context()`
- [x] normalize result shape for `get_signal_context()`
- [x] add tests for file-based live adapter loading
- [x] add documentation for file/HTTP live mode

## Still external to this repo
- [ ] connect real `query-token-info`
- [ ] connect real `crypto-market-rank`
- [ ] connect real `trading-signal`
- [ ] connect real `query-token-audit`
- [ ] connect real `query-address-info`
- [ ] connect real `meme-rush`
- [ ] deploy or wire a production OpenClaw/Binance adapter endpoint

## Final polish
- [x] add examples for live mode
- [x] add fallback path that can operate once a raw payload is available
- [ ] add richer user-facing fallback messaging for partially failed upstream calls
