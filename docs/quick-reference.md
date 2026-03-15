# Quick Reference

## Commands

### Live surface
| Command | Purpose |
|---------|---------|
| `/brief <symbol>` | Fast default asset read; can go deeper when data supports it |
| `/signal <symbol>` | Setup validation with invalidation and risk merged in |
| `/audit <symbol>` | Security-first token read with conditional meme lens |
| `/holdings [address]` | Portfolio posture or external wallet behavior, with posture + analytics + Alpha exposure |
| `/watchtoday` | Daily board with smart-money signals first and attention separated cleanly |

For a cleaner public-facing one-page version, see [`public-command-card.md`](public-command-card.md).

## API Endpoints (v0.2.1)

Current note:
- the canonical **public/product commands** are `brief`, `signal`, `audit`, `holdings`, and `watchtoday`
- supporting API/CLI paths such as `alpha` and `futures` may still exist, but they are not part of the locked main public surface

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | System status, version, config warnings |
| GET | `/runtime/report` | Extended runtime diagnostics |
| GET | `/brief?symbol=BNB` | Default asset brief |
| GET | `/brief?symbol=BNB&deep=true` | Deeper asset brief |
| GET | `/signal?token=DOGE` | Signal validation brief |
| GET | `/audit?symbol=BNB` | Security audit brief |
| GET | `/holdings` | Private portfolio posture |
| GET | `/holdings?address=0x...` | Wallet analysis brief |
| GET | `/watchtoday` | Daily market board |
| GET | `/alpha` | Binance Alpha overview |
| GET | `/alpha?symbol=RIVER` | Binance Alpha token detail |
| GET | `/futures?symbol=BTC` | Binance Futures positioning |

## Product promise
**Less noise. Better conviction.**

## What works especially well today
- Stronger trust / evidence honesty across the main commands
- Binance Spot read-only grounding for `/brief` and `/watchtoday`
- Supporting confirmation for deeper `/brief` and `/signal` reads
- `/holdings` is more behavior-aware and posture-aware
- Runtime health diagnostics in live mode via `/health`
- Live Binance Square posting with scheduled daily engine
- Security-hardened API (auth, rate limiting, SSRF protection, path traversal prevention)

## Output shape
- Compact product-style cards
- One-line header with symbol/market context where available
- Main state block (`Snapshot`, `Setup`, `Posture`, `Signals`, `Findings`)
- One-line verdict with dot markers
- One-line `⚠️` footer for compact risk/trust framing
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
- [`docs/live-command-mapping.md`](live-command-mapping.md)
- [`docs/deployment.md`](deployment.md)

## Local checks
```bash
make check
make test
```
