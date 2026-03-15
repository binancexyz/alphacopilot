# Bibipilot

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Less noise. Better conviction.

Bibipilot is a production-first crypto research and publishing copilot. The retained runtime surfaces are:

- CLI for the canonical research commands
- FastAPI REST API for rendered briefs
- Bridge API for raw runtime bundles
- Binance Square drafting and publishing tools

## Canonical product surface

| Command | Purpose |
|---------|---------|
| `brief <symbol>` | compact asset brief |
| `brief <symbol> deep` | deeper asset judgment |
| `signal <symbol>` | setup validation |
| `audit <symbol>` | security-first token brief |
| `holdings [address]` | portfolio or wallet posture |
| `watchtoday` | market board |

Secondary API endpoints `alpha` and `futures` remain available, but they are not part of the canonical command map.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python3 src/main.py brief BNB
make check
make test
```

## Configuration

Default mode is local-safe:

- `APP_ENV=development`
- `APP_MODE=mock`

Live mode requires:

- `BINANCE_SKILLS_BASE_URL`
- `BRIDGE_API_KEY` when the runtime adapter requires authenticated requests
- `BINANCE_API_KEY` and `BINANCE_API_SECRET` for account-backed portfolio flows

Public deployment requires:

- `API_AUTH_ENABLED=true`
- `API_AUTH_KEY`

Binance Square publishing requires:

- `BINANCE_SQUARE_API_KEY`

## Security posture

- Timing-safe API key comparison on the public API
- Optional dedicated bridge auth key instead of forwarding Binance account secrets
- Rate limiting
- Security headers on API and bridge responses
- Redirect-disabled live HTTP requests
- Path-constrained file-backed live mode
- Non-root Docker container

## Docs

- [`docs/install.md`](docs/install.md)
- [`docs/deployment.md`](docs/deployment.md)
- [`docs/quick-reference.md`](docs/quick-reference.md)
- [`docs/architecture.md`](docs/architecture.md)
- [`docs/binance-square-posting.md`](docs/binance-square-posting.md)
- [`docs/security-principles.md`](docs/security-principles.md)
- [`docs/maintainer-summary.md`](docs/maintainer-summary.md)
- [`docs/INDEX.md`](docs/INDEX.md)

## Notes

- Mock mode is kept for local development and tests.
- Demo-only docs and example payload exports were removed from the primary repo surface.
- This repo is a research and publishing system, not an autonomous trading engine.
