# `/signal` Live Design

## Why this is the next best command
- shares logic with `/token`
- strong demo value
- easier to implement than wallet or watch-today

## Required live skills
1. `trading-signal`
2. `query-token-info`
3. `query-token-audit`

## Runtime responsibilities (OpenClaw)
- parse the token input
- call the 3 live skills
- gather raw outputs
- pass them into the signal extractor/normalizer path

## Python responsibilities
- normalize into `SignalContext`
- interpret signal quality
- summarize fragility and risk
- build final brief

## Final output target
- Quick Verdict
- Signal Quality
- Top Risks
- Why It Matters
- What To Watch Next
- Risk Tags
- Conviction

## Suggested rollout
### Version 1
Live data + first-pass heuristics

### Version 2
Better conviction and invalidation logic
