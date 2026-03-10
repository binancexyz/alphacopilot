# Live Bridge Spec

This is the recommended production bridge contract for Bibipilot.

## Purpose
Provide a single HTTP adapter that invokes real Binance Skills and returns raw payload bundles to Bibipilot.

Bibipilot should not guess direct APIs in its main app flow. The bridge should own:
- Binance Skills invocation
- skill auth/runtime wiring
- raw response collection
- optional caching/retry behavior

Bibipilot should own:
- extraction
- normalization
- heuristics
- formatting
- Square-ready output generation

## Base URL
Example:
```text
https://your-bridge.example.com/runtime
```

Set in Bibipilot as:
```env
APP_MODE=live
BINANCE_SKILLS_BASE_URL=https://your-bridge.example.com/runtime
```

## Request model
### Supported commands
- `token`
- `wallet`
- `signal`
- `watchtoday`

### HTTP form
`GET /runtime?command=<command>&entity=<entity>`

Examples:
```text
GET /runtime?command=token&entity=BNB
GET /runtime?command=signal&entity=DOGE
GET /runtime?command=wallet&entity=0xabc...
GET /runtime?command=watchtoday
```

### Optional auth headers
- `X-API-Key`
- `X-API-Secret`

These are bridge-level headers, not Binance skill headers.

## Response model
Bridge may return either:
1. raw payload object directly
2. wrapped object under `raw`

Preferred response shape:
```json
{
  "command": "token",
  "entity": "BNB",
  "raw": {
    "query-token-info": {"...": "..."},
    "crypto-market-rank": {"...": "..."},
    "trading-signal": {"...": "..."},
    "query-token-audit": {"...": "..."}
  },
  "meta": {
    "source": "binance-skills-bridge",
    "generatedAt": "2026-03-10T00:00:00Z"
  }
}
```

## Command-to-skill mapping
### token
Required skills:
- `query-token-info`
- `crypto-market-rank`
- `trading-signal`
- `query-token-audit`

Entity:
- token symbol or contract-resolved token target

### signal
Required skills:
- `trading-signal`
- `query-token-info`
- `query-token-audit`

Entity:
- token symbol

### wallet
Required skills:
- `query-address-info`

Optional enrichment:
- `query-token-info`
- `crypto-market-rank`

Entity:
- wallet address

### watchtoday
Required skills:
- `crypto-market-rank`
- `meme-rush`
- `trading-signal`

Entity:
- none

## Bridge behavior rules
- call Binance Skills with their documented headers / request shapes
- keep skill invocation separate from Bibipilot interpretation
- return raw payloads as faithfully as possible
- preserve Binance field names
- do not compress away useful fields prematurely
- include partial results if one skill fails
- include clear bridge-level errors when a skill call fails

## Partial failure model
If one skill fails:
- return what succeeded
- include metadata for failed skill names
- let Bibipilot degrade confidence gracefully

Example:
```json
{
  "command": "token",
  "entity": "BNB",
  "raw": {
    "query-token-info": {"...": "..."},
    "trading-signal": {"...": "..."}
  },
  "meta": {
    "failedSkills": ["query-token-audit", "crypto-market-rank"]
  }
}
```

## Security requirements
- keep bridge secrets server-side only
- never expose Binance secrets in responses
- log failures without logging secret values
- rate-limit bridge if internet-facing
- prefer private-network deployment if possible

## Implementation order
1. token
2. signal
3. watchtoday
4. wallet
5. optional Square-post orchestration
6. spot only later and separately gated

## Important note
Bibipilot already supports this bridge pattern in `src/services/live_service.py`.
The main remaining work is building and deploying the bridge itself.
