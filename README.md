# Bibipilot

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![API v0.2.1](https://img.shields.io/badge/API-v0.2.1-orange.svg)](docs/deployment.md)
[![Bridge v0.2.0](https://img.shields.io/badge/Bridge-v0.2.0-orange.svg)](docs/openclaw-runtime-bridge.md)

> **Less noise. Better conviction.**

Bibipilot is a **Binance-native market, posture, and publishing intelligence copilot** that filters crypto signals, interprets risk, and publishes what is worth attention to Binance Square.

**research → judgment → posture → publishing**

It uses Binance Skills Hub as the evidence layer, adds a Python judgment layer on top, and turns useful output into Binance Square posts — including a premium scheduled daily publishing engine.

> **Status: public alpha — real command surface, live publishing, security-hardened API**
>
> Bibipilot now presents a 5-command canonical surface, live Binance Square publishing, a FastAPI REST service (v0.2.1), a live bridge for OpenClaw integration (v0.2.0), and production-grade security hardening. It is not finished, but it is well beyond concept stage.

---

## Table of contents

- [Why it exists](#why-bibipilot-exists)
- [What it does](#what-it-does)
- [What makes it different](#what-makes-it-different)
- [Architecture](#architecture)
- [Quick start](#quick-start)
- [Configuration](#configuration)
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

Bibipilot now has a clean **5-command canonical surface**:

| Command | What it answers |
|---------|------------------|
| `/brief <symbol>` | What matters about this asset right now? |
| `/signal <symbol>` | Is this setup real, risky, or breaking down? |
| `/holdings [address]` | What is this posture telling me? |
| `/watchtoday` | What deserves attention across the market today? |
| `/audit <symbol>` | Is this structurally safe enough to trust? |

That gives Bibipilot a very simple product story:
- **`/brief`** = flagship default read
- **`/signal`** = setup + risk + invalidation
- **`/holdings`** = private posture or external wallet behavior
- **`/watchtoday`** = market board
- **`/audit`** = safety read

`/brief <symbol> deep` is the richer asset-judgment path when you want more than the compact default answer.

For the cleanest one-page public explanation, see [`docs/public-command-card.md`](docs/public-command-card.md).

Publishing remains a first-class product output through Binance Square.

It also supports:
- **Binance Square publishing** — live text posting with draft/publish support
- **Scheduled daily posting** — premium 1-post/day engine centered on the nightly `night-diary` slot
- **REST API** — FastAPI service (v0.2.1) with auth, rate limiting, and security headers
- **Live bridge** — OpenClaw runtime bridge (v0.2.0) that powers the current product surface and supporting internal utilities

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

Bibipilot separates concerns into a few simple layers:

```
User (CLI / API / OpenClaw)
  → Parsing / validation
  → Data collection (mock or live)
  → Normalization
  → Analysis / judgment
  → Formatting
  → Output (terminal / API / Binance Square)
```

In practical terms:
- **OpenClaw / CLI / API** receives the request
- **services/** fetches or loads data
- **normalizers/extractors** make the payload shape consistent
- **analyzers/** decide what matters
- **formatters/** turn that into the final product voice

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

### 2. Try the product surface
```bash
python3 src/main.py brief BTC
python3 src/main.py brief BNB deep
python3 src/main.py signal DOGE
python3 src/main.py holdings
python3 src/main.py holdings 0x1234567890ab
python3 src/main.py audit BNB
python3 src/main.py watchtoday
```

### 3. Run checks
```bash
make check   # compile checks
make test    # test suite
```

### 4. Best first read if you want to collaborate
- `README.md`
- `docs/public-command-card.md`
- `docs/maintainer-summary.md`
- `docs/quick-reference.md`
- `docs/developer-flow.md`

---

## Configuration

Copy `.env.example` to `.env` and fill in values:
```bash
cp .env.example .env
```

### Core settings
| Variable | Default | Purpose |
|----------|---------|---------|
| `APP_ENV` | `development` | Environment name |
| `APP_MODE` | `mock` | `mock` for local dev, `live` for real data |
| `BINANCE_SKILLS_BASE_URL` | *(empty)* | Binance Skills adapter URL |
| `BINANCE_API_KEY` | *(empty)* | Binance API key for Spot data |
| `BINANCE_API_SECRET` | *(empty)* | Binance API secret |
| `COINMARKETCAP_API_KEY` | *(empty)* | Optional market quote source |

### API server settings
| Variable | Default | Purpose |
|----------|---------|---------|
| `API_HOST` | `0.0.0.0` | API listen address |
| `API_PORT` | `8000` | API listen port |
| `API_AUTH_ENABLED` | `false` | Enable HMAC API key auth |
| `API_AUTH_KEY` | *(empty)* | API key for `X-API-Key` header |
| `API_RATE_LIMIT_ENABLED` | `true` | Enable rate limiting |
| `API_RATE_LIMIT_REQUESTS` | `60` | Max requests per window |
| `API_RATE_LIMIT_WINDOW_SECONDS` | `60` | Rate limit window |

### Bridge settings
| Variable | Default | Purpose |
|----------|---------|---------|
| `BRIDGE_LIVE_ENABLED` | `false` | Enable live bridge |
| `BRIDGE_DEFAULT_CHAIN_ID` | `56` | Default chain (BSC) |
| `BRIDGE_HTTP_TIMEOUT_SECONDS` | `20` | HTTP timeout |
| `BRIDGE_HTTP_RETRIES` | `2` | Retry count |

### Binance Square settings
| Variable | Default | Purpose |
|----------|---------|---------|
| `BINANCE_SQUARE_API_KEY` | *(empty)* | Square publishing key |
| `BINANCE_SQUARE_API_BASE_URL` | `https://www.binance.com` | Square API base |

See [`.env.example`](.env.example) for the full template.

---

## API mode

Start the FastAPI REST server (v0.2.1):
```bash
make api
# or directly:
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

### Endpoints

Current note:
- the **CLI/product surface** and **REST API** are now aligned around the same canonical five-command map

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | System status, version, config warnings |
| GET | `/runtime/report` | Extended runtime diagnostics |
| GET | `/brief?symbol=BNB` | Default asset brief |
| GET | `/brief?symbol=BNB&deep=true` | Deeper asset brief |
| GET | `/signal?token=DOGE` | Signal validation brief |
| GET | `/audit?symbol=BNB` | Security audit brief |
| GET | `/holdings` | Private portfolio posture |
| GET | `/holdings?address=0x...` | Wallet behavior read |
| GET | `/watchtoday` | Daily market board |

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
Provides a single `/runtime` endpoint for OpenClaw integration. Pass `command` and `entity` as query parameters:
```
GET /runtime?command=token&entity=BNB
GET /runtime?command=signal&entity=DOGE
GET /runtime?command=audit&entity=BNB
GET /runtime?command=meme&entity=DOGE
GET /runtime?command=watchtoday
GET /runtime?command=wallet&entity=0x...
```
The bridge also exposes `/health` for readiness checks.

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
- 5-command canonical surface with structured output (read, conviction, risks, watch, context)
- Trust and evidence honesty across the main commands
- Binance Spot read-only grounding for `brief` and `watchtoday`, with supporting confirmation where deeper reads allow it
- Unified posture read via `/holdings`
- Runtime health diagnostics via `/health`
- Live Binance Square posting with scheduled daily engine
- API security hardening (auth, rate limiting, SSRF protection, path traversal prevention, security headers)

### Where collaborators should focus next
- improve live/runtime depth
- improve external-wallet evidence quality inside `/holdings`
- improve speculative/meme-style context where it strengthens `/audit`
- keep sharpening `/brief` and `/watchtoday` from real usage

### What this is not
- not an autonomous trading bot
- not a giant dashboard product
- not feature-complete yet

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

### If you are new here
Start in this order:
1. `README.md`
2. `docs/maintainer-summary.md`
3. `docs/quick-reference.md`
4. `docs/developer-flow.md`
5. `docs/INDEX.md`

### Project layout
```
bibipilot/
├── src/
│   ├── main.py              # Canonical CLI entry point
│   ├── api.py               # Canonical REST API
│   ├── bridge_api.py        # OpenClaw runtime bridge
│   ├── analyzers/           # Product judgment logic
│   ├── formatters/          # Final output rendering
│   ├── models/              # Shared schemas
│   ├── services/            # Data loading + integrations
│   └── utils/               # Parsing, validation, helpers
├── tests/                   # Regression and API tests
├── docs/                    # Product, runtime, and handoff docs
├── examples/                # Output examples and payload samples
├── agent/                   # Agent identity and operating files
├── scripts/                 # Deployment and utility scripts
├── Dockerfile               # Python 3.12-slim, non-root container
├── Makefile                 # Common development targets
└── pyproject.toml           # Package metadata
```

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
| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.10+ (3.12 in Docker) |
| API framework | FastAPI | 0.135.1 |
| ASGI server | uvicorn | 0.41.0 |
| HTTP client | httpx | 0.28.1 |
| Terminal formatting | rich | 13.7.1 |
| Configuration | python-dotenv | 1.2.2 |

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
