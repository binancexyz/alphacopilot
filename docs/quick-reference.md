# Quick Reference

## Commands
- `/price <symbol>` — compact market card, prefers Binance Spot read-only data when available
- `/brief <symbol>` — fast synthesis with exchange-native market grounding when available
- `/token <symbol>` — token setup / conviction read with Spot as supporting confirmation
- `/signal <token>` — setup validation that separates exchange price from matched signal quality
- `/wallet <address>` — wallet behavior / follow verdict
- `/watchtoday` — daily board with Exchange Board + signal / narrative lanes
- `/meme <symbol>` — first-pass meme read
- `careers` — Binance ecosystem/company-priority pulse

## Product promise
**Less noise. Better conviction.**

## What works especially well today
- stronger trust / evidence honesty across the main commands
- Binance Spot read-only grounding for `price`, `brief`, and `watchtoday`
- supporting Binance Spot confirmation for `token` and `signal`
- wallet output is more behavior-aware than before
- runtime health diagnostics exist in live mode via `/health`

## Output shape
- Quick Verdict
- Signal Quality / Conviction
- Top Risks
- Why It Matters
- What To Watch Next
- Risk Tags / lane coverage when relevant

## Best first docs
- `README.md`
- `docs/INDEX.md`
- `docs/demo-script.md`
- `docs/binance-spot-integration.md`
- `docs/commands-overview.md`
- `docs/production-readiness.md`

## Local checks
```bash
make check
make test
```
