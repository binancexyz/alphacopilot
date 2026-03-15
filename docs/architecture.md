# Architecture

Bibipilot is organized around a production runtime boundary:

```text
CLI / REST API / Bridge / Square CLI
  -> parsing + validation
  -> data access services
  -> extractors + normalizers
  -> analyzers
  -> formatters / post builders
```

## Runtime surfaces
- `src/main.py`: canonical CLI for `brief`, `signal`, `audit`, `holdings`, `watchtoday`
- `src/api.py`: rendered REST API for the same product surface plus secondary `alpha` and `futures`
- `src/bridge_api.py`: raw bundle bridge for runtime integrations
- `src/square_cli.py` and `src/square_diary.py`: Binance Square drafting and publishing

## Service boundary
- `src/services/factory.py` selects `mock` or `live` mode from `APP_MODE`.
- `src/services/live_service.py` is the only runtime adapter for live bundle fetching.
- `src/services/mock_service.py` keeps local development and tests deterministic.
- `src/services/live_extractors.py` and `src/services/normalizers.py` convert raw payloads into stable analysis input.

## Domain boundary
- `src/analyzers/` contains command-specific judgment logic.
- `src/models/` defines shared output types.
- `src/formatters/` renders terminal and API-facing presentation.

## External dependencies
- Binance Skills-style runtime adapter via `BINANCE_SKILLS_BASE_URL`
- Binance account APIs for portfolio-backed flows that require `BINANCE_API_KEY` and `BINANCE_API_SECRET`
- Binance Square publish endpoint for post creation
- Optional market enrichment via CoinMarketCap

## Security model
- The main API uses timing-safe API key comparison and rate limiting.
- The bridge can use a dedicated `BRIDGE_API_KEY` instead of reusing Binance account secrets.
- Live HTTP calls reject non-HTTP(S) schemes and disable redirects.
- File-backed live mode constrains payload reads to the configured base directory.
- Docker runs as a non-root user.

## Command posture
- Canonical product surface: `brief`, `signal`, `audit`, `holdings`, `watchtoday`
- Secondary API surface: `alpha`, `futures`
- Development-only scaffolding should not define the production architecture
