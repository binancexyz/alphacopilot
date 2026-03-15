# Maintainer Summary

## Current scope
- Canonical product surface: `brief`, `signal`, `audit`, `portfolio`, `wallet`, `watchtoday`, `alpha`, `futures`
- Compatibility aliases: `holdings`
- Production runtime surfaces kept in repo: CLI, REST API, bridge API, Square publishing

## Repo rules
- Keep docs operator-focused; avoid rebuilding large historical, demo, or submission doc trees.
- Keep bridge auth separate from Binance account credentials.
- Update `pyproject.toml`, `src/version.py`, and FastAPI app versions together.
- If a script or Make target does not map to a live command surface, remove it instead of documenting it.

## Runtime assumptions
- `APP_MODE=mock` is the default local mode.
- `APP_MODE=live` depends on `BINANCE_SKILLS_BASE_URL`.
- Portfolio-backed flows depend on `BINANCE_API_KEY` and `BINANCE_API_SECRET`.
- Public deployment depends on `API_AUTH_ENABLED=true` and `API_AUTH_KEY`.

## Quality baseline
- `make check`
- `make test`
- Smoke test the CLI, `/health`, and bridge `/runtime` before release.
