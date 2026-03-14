# `/token` Live Design

This is the best first real live integration target.

## Why start with `/token`
- easiest command to explain
- strongest demo value
- uses the clearest cross-skill combination
- good foundation for later `/signal`

## User Input
Examples:
- `/token BNB`
- `/token PEPE`
- `/token DOGE`

## Required live skills
1. `query-token-info`
2. `crypto-market-rank`
3. `trading-signal`
4. `query-token-audit`

## Runtime responsibilities (OpenClaw)
- parse the command
- resolve the symbol
- call all 4 live skills
- gather raw responses
- pass raw responses into a normalizer/extractor

## Python responsibilities
- normalize raw responses into `TokenContext`
- interpret signal quality
- summarize major risks
- generate risk tags
- compute conviction label
- format the final brief

## Raw-to-normalized mapping target

### From `query-token-info`
Use for:
- symbol
- display_name
- price
- liquidity
- holders

### From `crypto-market-rank`
Use for:
- market_rank_context
- major_risks related to overheating / narrative quality

### From `trading-signal`
Use for:
- signal_status
- signal_trigger_context
- signal-related risks

### From `query-token-audit`
Use for:
- audit_flags
- contract-related risks

## Example final normalized shape
```python
{
  "symbol": "BNB",
  "display_name": "BNB",
  "price": 612.5,
  "liquidity": 125000000.0,
  "holders": 1850000,
  "market_rank_context": "Large-cap token with strong liquidity and ecosystem relevance.",
  "signal_status": "watch",
  "signal_trigger_context": "Momentum improving but confirmation is incomplete.",
  "audit_flags": [],
  "major_risks": [
    "Signal may weaken if volume does not confirm.",
    "Broader market weakness can reduce follow-through."
  ]
}
```

## Final output target
The user should see:
- Quick Verdict
- Signal Quality
- Top Risks
- Why It Matters
- What To Watch Next
- Risk Tags
- Conviction

## Suggested rollout
### Version 1
Live token data + current scaffold heuristics

### Version 2
Smarter signal-quality scoring from real fields

### Version 3
Better risk tags and beginner/pro mode
