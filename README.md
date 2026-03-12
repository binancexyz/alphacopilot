# Bibipilot

> **Less noise. Better conviction.**

Bibipilot is a **Binance-native research copilot** that filters crypto signals, interprets risk, and publishes what is worth attention to Binance Square.

**research → judgment → publishing**

It uses Binance Skills Hub as the evidence layer, adds a Python judgment layer on top, and turns useful output into Binance Square posts — including a premium scheduled daily publishing engine.

> **Status: public alpha — real command surface, live publishing, security-hardened API**
>
> Bibipilot has 10 research commands, live Binance Square publishing, a FastAPI REST service (v0.2.1), a live bridge for OpenClaw integration (v0.2.0), and production-grade security hardening. It is not finished, but it is well beyond concept stage.

---

## Table of contents

- [Why it exists](#why-bibipilot-exists)
- [What it does](#what-it-does)
- [What makes it different](#what-makes-it-different)
- [Architecture](#architecture)
- [Quick start](#quick-start)
- [API mode](#api-mode)
- [Docker](#docker)
- [Binance Square publishing](#binance-square-publishing)
- [Mock mode vs live mode](#mock-mode-vs-live-mode)
- [Current status](#current-status)
- [Safety posture](#safety-posture)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

---

## Why Bibipilot exists

Crypto users can already find plenty of raw movement — token activity, wallet flows, smart-money signals, trending sectors, risk tools. The harder part is deciding:

- what is real
- what is risky
- what is late
- what is worth publishing

Bibipilot is designed for that gap. It does not try to be a full autonomous trading system. It is the layer between **raw crypto signals** and **usable conviction**.

---

## What it does

Bibipilot currently supports **10 research commands**:

| Command | Purpose |
|---------|---------|
| `/price <symbol>` | Compact market card with Binance Spot read-only data |
| `/brief <symbol>` | Fast market synthesis with exchange-native grounding |
| `/token <symbol>` | Token setup and conviction read with audit and signal context |
| `/signal <token>` | Smart-money signal timing and setup validation |
| `/wallet <address>` | Wallet behavior interpretation with follow verdict |
| `/risk <symbol>` | Downside-first risk assessment |
| `/audit <symbol>` | Security-first token audit card |
| `/watchtoday` | Daily market board with trending narratives and live lanes |
| `/meme <symbol>` | First-pass meme token scan |
| `careers` | Binance hiring pulse for ecosystem intelligence |

It also supports:
- **Binance Square publishing** — live text posting with draft/publish support
- **Scheduled daily posting** — premium 1-post/day engine centered on the nightly `night-diary` slot
- **REST API** — FastAPI service (v0.2.1) with auth, rate limiting, and security headers
- **Live bridge** — OpenClaw runtime integration (v0.2.0) for token, signal, audit, meme, and watchtoday

---

## What makes it different

### 1. Real judgment layer
Bibipilot does not stop at surfacing movement. It answers: should I care? Should I trust this? Should I avoid this? Should this be published?

### 2. Binance-native
Built around Binance Skills Hub for evidence, Binance Spot for exchange-native price grounding, and Binance Square for publishable output.

### 3. Real publishing loop
Not just an analysis interface — it can publish live posts to Binance Square and includes a scheduled premium daily posting engine with context-aware topic selection and distinct diary / builder / market night modes.

### 4. Command-specific design
Each command is shaped for its own job rather than forcing everything into one generic answer template.

### 5. Security-hardened
API authentication (HMAC timing-safe), rate limiting, SSRF protection, path traversal prevention, security headers, and non-root container defaults.

---

## Architecture

Bibipilot separates concerns into independent layers:

```
User (CLI / API / OpenClaw)
  → Parser (normalize token symbols, wallet addresses)
  → Service Factory (select mock or live mode)
  → Market Data Service (Binance Skills Hub / Binance Spot / mock)
  → Normalizers (standardize payload structure)
  → Analyzers (build AnalysisBrief with conviction and risk assessment)
  → Formatters (render to terminal with rich styling)
  → Output (console / Binance Square post / API response)
```

### Evidence layer — Binance Skills Hub
| Skill | Purpose |
|-------|---------|
| `query-token-info` | Token metadata, market data, K-Line |
| `query-token-audit` | Security scan, scam/contract risk |
| `query-address-info` | Wallet holdings and portfolio |
| `trading-signal` | Smart-money buy/sell signals |
| `crypto-market-rank` | Trending, alpha, smart-money inflow |
| `meme-rush` | Meme lifecycle, holder distribution |

### Supporting data
- **Binance Spot API** — read-only price, spread, and 24h change (optional)
- **CoinMarketCap API** — supplemental market quotes (optional)
- **Binance Careers API** — ecosystem hiring data (optional)

### Output layer
- `square-post` — Binance Square publishing
- Rich terminal formatting via the `rich` library
- FastAPI JSON responses

### Deferred execution
- `spot` — kept disabled/deferred by default, requires explicit human confirmation

---

## Quick start

### 1. Clone and install
```bash
git clone https://github.com/binancexyz/bibipilot.git
cd bibipilot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. CLI usage
```bash
python3 src/main.py price BNB
python3 src/main.py brief BTC
python3 src/main.py token BNB
python3 src/main.py signal DOGE
python3 src/main.py wallet 0x1234567890ab
python3 src/main.py risk ETH
python3 src/main.py audit BNB
python3 src/main.py watchtoday
python3 src/main.py meme DOGE
python3 src/main.py careers
python3 src/main.py careers --cache-only
```

### 3. Run checks
```bash
make check   # compile checks
make test    # test suite
```

---

## API mode

Start the FastAPI REST server (v0.2.1):
```bash
make api
# or directly:
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

### Endpoints

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

### Security middleware
- Optional API key authentication (`X-API-Key` header, HMAC timing-safe comparison)
- Configurable rate limiting (requests per time window)
- Security headers (`X-Content-Type-Options`, `X-Frame-Options`, `Cache-Control`)
- CORS middleware (disabled by default — safe posture)
- Optional request logging

### Live bridge API (v0.2.0)
```bash
make bridge-api
```
Provides OpenClaw runtime integration endpoints for token, signal, audit, meme, and watchtoday. Wallet bridge is scaffolded.

---

## Docker

```bash
# Build
docker build -t bibipilot .

# Run in mock mode
docker run --rm -p 8000:8000 -e APP_MODE=mock bibipilot

# Run in live mode
docker run --rm -p 8000:8000 \
  -e APP_MODE=live \
  -e BINANCE_SKILLS_BASE_URL=https://adapter.example.com/runtime \
  -e BINANCE_API_KEY=... \
  -e BINANCE_API_SECRET=... \
  bibipilot
```

Container runs Python 3.12-slim as a non-root `appuser` on port 8000.

---

## Binance Square publishing

Bibipilot includes a complete publishing pipeline:

- **Live Binance Square posting** — publish text posts directly
- **Draft/publish support** — editorial control before posting
- **Scheduled premium 1-post/day engine** — cron-driven nightly publishing via `night-diary` at `21:30` Asia/Phnom_Penh
- **Context-aware topic selection** — weighs fresh repo/work context instead of simple slot rotation
- **Night-mode variation** — adapts tone between diary / builder / market modes
- **Git integration** — pulls recent commit context into the nightly post generator
- **Performance logging** — tracks post metrics and writing seeds

### Publishing commands
```bash
# Draft a token analysis post
python3 src/square_cli.py token BNB

# Draft and publish directly
python3 src/square_cli.py token BNB --publish

# Run the nightly diary engine
python3 src/square_diary.py night-diary

# Makefile shortcuts
make square-draft    # draft mode
make square-publish  # publish mode
make diary-night     # nightly diary
```

---

## Mock mode vs live mode

### Mock mode (default: `APP_MODE=mock`)
- Local development and testing
- Stable demos without live dependencies
- Formatter and analyzer testing

### Live mode (`APP_MODE=live`)
- Real Binance Skills Hub integration
- Live payload extraction and normalization
- Binance Square publishing flows
- Binance Spot read-only market grounding

Current live bridge coverage is strongest for `token`, `signal`, `audit`, and `watchtoday`. Wallet and meme quality still depend on thinner live context.

The careers pulse is deliberately separate from token/signal logic — treat it as ecosystem intelligence, not a direct trading signal.

---

## Current status

### What works well
- 10 research commands with structured output (verdict, conviction, risks, what to watch)
- Trust and evidence honesty across core commands
- Binance Spot read-only grounding for `price`, `brief`, `watchtoday`, and supporting confirmation in `token` / `signal`
- Behavior-aware wallet analysis
- Runtime health diagnostics via `/health`
- Live Binance Square posting with scheduled daily engine
- API security hardening (auth, rate limiting, SSRF protection, path traversal prevention, security headers)

### What is still evolving
- Live bridge coverage is strongest for `token`, `signal`, `audit`, and `watchtoday`
- `wallet` and `meme` depend on thinner live runtime context
- Binance Careers is an adjacent ecosystem-intelligence lane
- This is a public alpha research copilot, not a finished autonomous trading system

---

## Safety posture

Bibipilot is:
- **Read-oriented** — no execution features enabled
- **Research-first** — analysis over action
- **Human-supervised** — outputs require human judgment
- **Risk-aware** — risks visible by default, no fake certainty

It should **not** be described as a finished autonomous trading system.

If you work on this repo:
- Never commit secrets — keep `.env` private
- Keep risk visible in outputs
- Prefer lower-confidence wording when live context is incomplete

See also: [`SECURITY.md`](SECURITY.md) and [`SECURITY-CHECKLIST.md`](SECURITY-CHECKLIST.md)

---

## Documentation

### Start here
| Document | Purpose |
|----------|---------|
| [`docs/INDEX.md`](docs/INDEX.md) | Full documentation index |
| [`docs/prd.md`](docs/prd.md) | Product requirements document |
| [`docs/architecture.md`](docs/architecture.md) | System design and layer separation |
| [`docs/quick-reference.md`](docs/quick-reference.md) | Command reference and output shape |
| [`docs/commands-overview.md`](docs/commands-overview.md) | Detailed command documentation |
| [`docs/install.md`](docs/install.md) | Installation and setup |
| [`docs/deployment.md`](docs/deployment.md) | Docker and deployment guide |

### Deep dives
| Document | Purpose |
|----------|---------|
| [`docs/binance-spot-integration.md`](docs/binance-spot-integration.md) | Exchange data grounding |
| [`docs/skill-command-matrix.md`](docs/skill-command-matrix.md) | Skills-to-commands mapping |
| [`docs/demo-script.md`](docs/demo-script.md) | Complete demo walkthrough |
| [`docs/roadmap.md`](docs/roadmap.md) | Product roadmap |
| [`examples/current-output-examples.md`](examples/current-output-examples.md) | Fresh CLI output examples |

### Tech stack
- **Python 3.10+** (3.12 in Docker)
- **FastAPI** and **uvicorn** — REST API
- **httpx** — HTTP client
- **rich** — terminal formatting
- **python-dotenv** — environment configuration

---

## Contributing

Contributions that improve these areas are especially useful:
- live integration wiring
- normalized payload extraction
- output and heuristic quality
- documentation clarity
- maintainability

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for details.

Before opening a PR:
```bash
make check
make test
```

---

## License

MIT
