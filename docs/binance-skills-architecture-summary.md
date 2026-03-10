# Binance Skills Architecture Summary

This is the cleanest current model of how Alpha Copilot should use Binance Skills.

## Core principle
Alpha Copilot should integrate with Binance primarily through the **Skills/runtime model**, not by guessing ad hoc REST endpoints.

The preferred flow is:
1. OpenClaw/runtime invokes Binance Skills
2. raw skill outputs are collected
3. Python extracts and normalizes the raw payloads
4. analyzers interpret signal, risk, and conviction
5. formatters produce the final brief or Square-ready output

## Skill roles

### 1. `query-token-info`
Primary token facts + real-time market data + charts.

Use for:
- token search and resolution
- metadata and social links
- creator/project context
- price, volume, market cap, liquidity, holders
- K-Line chart data

### 2. `query-token-audit`
Primary safety gate.

Use for:
- honeypot / scam / malicious contract detection
- buy/sell tax checks
- verification status
- structured contract/trade/scam risks

Important rule:
Only trust/display audit output when `hasResult=true` and `isSupported=true`.
LOW risk is not the same as safe.

### 3. `query-address-info`
Wallet inventory layer.

Use for:
- wallet holdings
- token balances and quantities
- price and 24h change per held token
- portfolio breakdown inputs

### 4. `crypto-market-rank`
Broad discovery and market-intelligence layer.

Use for:
- trending tokens
- top search
- Binance Alpha picks
- stock-token discovery
- social hype summaries
- smart money inflow ranking
- meme ranking
- trader/KOL PnL leaderboards

### 5. `meme-rush`
Meme lifecycle + topic intelligence layer.

Use for:
- new/finalizing/migrated meme launches
- launchpad/protocol context
- dev behavior and wash-trading filters
- holder distribution risk
- Topic Rush / narrative inflow tracking

### 6. `trading-signal`
Smart money timing + signal quality layer.

Use for:
- smart money buy/sell signals
- trigger price vs current price
- max gain and exit rate
- active vs timeout vs completed signal interpretation
- token tag and launch-platform context

### 7. `square-post`
Required publishing/output skill.

Use for:
- turning research output into Binance Square-ready posts
- posting concise public summaries

This is a must-have product capability, not an optional extra.

### 8. `spot`
Deferred higher-risk exchange/execution skill.

Use for later:
- public spot market data
- authenticated account reads
- trading and advanced order workflows

This should stay behind explicit confirmation and stronger safety controls.

## Product layers

### Research core
- `query-token-info`
- `query-token-audit`
- `query-address-info`
- `crypto-market-rank`
- `meme-rush`
- `trading-signal`

### Output core
- `square-post`

### Execution layer (deferred)
- `spot`

## Best command-to-skill mapping

### `/token <symbol>`
- `query-token-info`
- `crypto-market-rank`
- `trading-signal`
- `query-token-audit`

### `/wallet <address>`
- `query-address-info`
- optional enrichment from `query-token-info`
- optional market/trader context from `crypto-market-rank`

### `/watchtoday`
- `crypto-market-rank`
- `meme-rush`
- `trading-signal`

### `/signal <token>`
- `trading-signal`
- `query-token-info`
- `query-token-audit`

### Square output
- `square-post`

## Important implementation rules
- keep runtime/raw collection separate from interpretation
- parse numeric strings carefully
- prefix Binance static icon paths with `https://bin.bnbstatic.com`
- use the documented User-Agent per skill
- do not turn audit output into investment advice
- keep research-first posture even when signal quality looks strong
- gate any `spot` execution path behind explicit human confirmation

## Current product stance
Alpha Copilot should be:
- research-first
- signal-and-risk oriented
- Square-output capable
- human-supervised
- cautious about execution features
