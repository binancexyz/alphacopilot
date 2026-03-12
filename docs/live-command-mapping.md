# Live Command Mapping

This document defines the exact live integration plan for each canonical command.

## `/brief <symbol>`

### Live skills to call
1. `query-token-info`
2. `crypto-market-rank`
3. `trading-signal`
4. `query-token-audit` (for deeper path when needed)

### OpenClaw responsibility
- accept user input
- resolve token symbol/name
- call Binance Skills Hub tools
- collect raw outputs
- normalize into one asset context payload

### Python responsibility
- interpret signal quality
- synthesize risk summary
- generate confidence framing
- format the fast default brief

### Minimum normalized fields
- symbol
- display_name
- price
- liquidity
- market_rank_context
- signal_status
- major_risks

---

## `/brief <symbol> deep`

### Live skills to call
1. `query-token-info`
2. `crypto-market-rank`
3. `trading-signal`
4. `query-token-audit`

### Python responsibility
- assign conviction label
- generate deeper risk/watch structure
- produce the richer asset brief

---

## `/holdings <address>`

### Live skills to call
1. `query-address-info`
2. optional `query-token-info` for top holdings
3. optional `query-token-audit` for concentrated risky holdings

### OpenClaw responsibility
- validate wallet input
- fetch address info
- identify top holdings
- optionally enrich top holdings
- normalize into wallet context payload

### Python responsibility
- interpret behavior pattern
- summarize concentration risk
- infer narrative dependence
- produce risk-aware explanation

### Minimum normalized fields
- address
- portfolio_value
- holdings_count
- top_holdings
- top_concentration_pct
- change_24h
- notable_exposures
- major_risks

---

## `/holdings`

### Live skills to call
1. signed Binance account-read endpoints
2. live price map / supporting spot data

### OpenClaw responsibility
- fetch private Spot balances
- normalize balances and LD-style holdings
- pass posture snapshot into Python

### Python responsibility
- compute posture
- summarize concentration and grouped exposures
- describe freshness and drift

---

## `/watchtoday`

### Live skills to call
1. `crypto-market-rank`
2. `meme-rush`
3. `trading-signal`

### OpenClaw responsibility
- fetch top narratives
- fetch active meme trends
- fetch strongest signal context
- normalize into watch-today context payload

### Python responsibility
- prioritize narratives
- separate signal from noise
- identify risk zones
- summarize the daily takeaway

### Minimum normalized fields
- top_narratives
- strongest_signals
- risk_zones
- market_takeaway
- major_risks

---

## `/signal <token>`

### Live skills to call
1. `trading-signal`
2. `query-token-info`
3. `query-token-audit`

### OpenClaw responsibility
- resolve token input
- fetch signal data
- fetch token context
- fetch audit context
- normalize into signal context payload

### Python responsibility
- interpret signal strength
- explain fragility
- define confirmation / invalidation conditions
- format a concise brief

### Minimum normalized fields
- token
- signal_status
- trigger_price
- current_price
- max_gain
- exit_rate
- audit_flags
- major_risks
- supporting_context

---

## `/audit <symbol>`

### Live skills to call
1. `query-token-audit`
2. `query-token-info`
3. optional `meme-rush` when speculative/lifecycle context is useful

### Python responsibility
- interpret structural safety
- surface audit validity clearly
- fold meme-lens context into audit findings when relevant
