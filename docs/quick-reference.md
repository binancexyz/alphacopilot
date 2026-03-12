# Quick Reference

## Commands

### Canonical
| Command | Purpose |
|---------|---------|
| `/brief <symbol>` | Fast default asset read; can go deeper when data supports it |
| `/signal <symbol>` | Setup validation with invalidation and risk merged in |
| `/holdings [address]` | Portfolio posture or external wallet behavior |
| `/watchtoday` | Daily board with Exchange Board + signal / narrative lanes |
| `/audit <symbol>` | Security-first token read with meme lens folded in |

### Hidden compatibility
| Older command | New home |
|---------|---------|
| `/token <symbol>` | `/brief <symbol> deep` |
| `/portfolio` | `/holdings` |
| `/wallet <address>` | `/holdings <address>` |
| `/risk <symbol>` | `/signal <symbol>` |
| `/meme <symbol>` | `/audit <symbol>` |
| `/price <symbol>` | hidden utility surface |
| `/watch` | removed alias |
| `careers` | removed from main product surface |

## API Endpoints (v0.2.1)

Current note:
- canonical **CLI/product commands** are `brief`, `signal`, `holdings`, `watchtoday`, and `audit`
- some API routes still use older compatibility naming

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | System status, version, config warnings |
| GET | `/runtime/report` | Extended runtime diagnostics |
| GET | `/brief/token?symbol=BNB` | Deeper asset brief (compatibility route) |
| GET | `/brief/signal?token=DOGE` | Signal validation brief |
| GET | `/brief/audit?symbol=BNB` | Security audit brief |
| GET | `/brief/meme?symbol=DOGE` | Specialist meme brief (compatibility route) |
| GET | `/brief/wallet?address=0x...` | Wallet analysis brief (compatibility route; CLI uses `holdings`) |
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
