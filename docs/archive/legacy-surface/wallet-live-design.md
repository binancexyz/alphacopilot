# `/wallet` Live Design

## Required live skills
1. `query-address-info`
2. optional `query-token-info` for top holdings
3. optional `query-token-audit` for concentrated risky holdings

## Runtime responsibilities
- validate wallet input
- fetch address context
- optionally enrich top holdings
- pass payload to normalizer

## Python responsibilities
- interpret concentration
- summarize notable exposures
- produce risk-aware wallet brief
