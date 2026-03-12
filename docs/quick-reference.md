# Quick Reference

## Commands

### Core
| Command | Purpose |
|---------|---------|
| `/brief <symbol>` | Fast default market read with source/context framing |
| `/token <symbol>` | Token setup / conviction read with Spot as supporting confirmation |
| `/signal <token>` | Setup validation with invalidation and matched-signal separation |
| `/portfolio` | Private Binance Spot posture with freshness/history-aware drift |
| `/wallet <address>` | Wallet behavior / follow verdict |
| `/watchtoday` | Daily board with Exchange Board + signal / narrative lanes |

### Specialist
| Command | Purpose |
|---------|---------|
| `/price <symbol>` | Premium market utility card |
| `/risk <symbol>` | Downside-first risk assessment |
| `/audit <symbol>` | Security-first token audit card |
| `/meme <symbol>` | First-pass meme read |
| `careers` | Binance ecosystem/company-priority pulse |

## API Endpoints (v0.2.1)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | System status, version, config warnings |
| GET | `/runtime/report` | Extended runtime diagnostics |
| GET | `/brief/token?symbol=BNB` | Token analysis brief |
| GET | `/brief/signal?token=DOGE` | Signal validation brief |
| GET | `/brief/audit?symbol=BNB` | Security audit brief |
| GET | `/brief/meme?symbol=DOGE` | Meme token brief |
| GET | `/brief/wallet?address=0x...` | Wallet analysis brief |
| GET | `/brief/watchtoday` | Daily market board |

## Product promise
**Less noise. Better conviction.**

## What works especially well today
- Stronger trust / evidence honesty across the main commands
- Binance Spot read-only grounding for `price`, `brief`, and `watchtoday`
- Supporting Binance Spot confirmation for `token` and `signal`
- Wallet output is more behavior-aware
- Runtime health diagnostics in live mode via `/health`
- Live Binance Square posting with scheduled daily engine
- Security-hardened API (auth, rate limiting, SSRF protection, path traversal prevention)

## Output shape
- Structured section-based layout
- Read / Verdict / Risks / Watch blocks where appropriate
- Context / Source / Validity tags when relevant
- Command-specific additions like `Invalidation` for `/signal`
- Premium tree-style hierarchy for grouped outputs

## Publishing commands
```bash
python3 src/square_cli.py token BNB             # draft
python3 src/square_cli.py token BNB --publish    # publish
python3 src/square_diary.py night-diary          # scheduled diary
```

## Best first docs
- [`README.md`](../README.md)
- [`docs/INDEX.md`](INDEX.md)
- [`docs/prd.md`](prd.md)
- [`docs/architecture.md`](architecture.md)
- [`docs/commands-overview.md`](commands-overview.md)
- [`docs/demo-script.md`](demo-script.md)
- [`docs/binance-spot-integration.md`](binance-spot-integration.md)
- [`docs/deployment.md`](deployment.md)

## Local checks
```bash
make check
make test
```
