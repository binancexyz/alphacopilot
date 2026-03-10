# Live Adapter Implementation

This document translates the live integration plan into concrete implementation tasks.

## Goal
Connect real Binance Skills Hub / OpenClaw runtime outputs into the normalized Python context layer.

## Strategy
Use OpenClaw to gather live tool outputs, then pass structured payloads into Python normalizers and analyzers.

## Token Adapter
### Inputs needed
- token info
- market rank context
- trading signal
- token audit

### Target method
`get_token_context(symbol: str) -> dict`

### Implementation steps
1. Resolve token symbol/name from user input
2. Call `query-token-info`
3. Call `crypto-market-rank`
4. Call `trading-signal`
5. Call `query-token-audit`
6. Extract the fields needed by `TokenContext`
7. Return a normalized dict

### Output fields
- symbol
- display_name
- price
- liquidity
- holders
- market_rank_context
- signal_status
- signal_trigger_context
- audit_flags
- major_risks

## Wallet Adapter
### Inputs needed
- address info
- optional token enrichment for top holdings
- optional audit context for concentrated risky positions

### Target method
`get_wallet_context(address: str) -> dict`

### Implementation steps
1. Validate address
2. Call `query-address-info`
3. Extract top holdings and concentration
4. Optionally enrich top positions
5. Build major risk list
6. Return normalized dict

### Output fields
- address
- portfolio_value
- holdings_count
- top_holdings
- top_concentration_pct
- change_24h
- notable_exposures
- major_risks

## Watch Today Adapter
### Inputs needed
- market rank context
- meme rush context
- trading signal context

### Target method
`get_watch_today_context() -> dict`

### Implementation steps
1. Call `crypto-market-rank`
2. Call `meme-rush`
3. Call `trading-signal`
4. Prioritize top narratives and strongest signals
5. Define main risk zones
6. Return normalized dict

### Output fields
- top_narratives
- strongest_signals
- risk_zones
- market_takeaway
- major_risks

## Signal Adapter
### Inputs needed
- trading signal
- token context
- token audit

### Target method
`get_signal_context(token: str) -> dict`

### Implementation steps
1. Resolve token input
2. Call `trading-signal`
3. Call `query-token-info`
4. Call `query-token-audit`
5. Build signal support + fragility context
6. Return normalized dict

### Output fields
- token
- signal_status
- trigger_price
- current_price
- max_gain
- exit_rate
- audit_flags
- supporting_context
- major_risks

## Important rule
The adapter should collect and normalize.
The analyzer should interpret.
Do not mix both responsibilities.
