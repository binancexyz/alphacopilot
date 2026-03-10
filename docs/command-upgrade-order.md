# Command Upgrade Order

## Already upgraded furthest
1. `/token`

## Best next order
2. `/signal`
3. `/wallet`
4. `/watchtoday`

## Why
- `/signal` reuses token-related logic
- `/wallet` needs more behavior interpretation
- `/watchtoday` is broadest and benefits from stronger primitives first
