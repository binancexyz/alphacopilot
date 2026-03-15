# Security Principles

## Required controls
- Keep the public API behind `API_AUTH_ENABLED=true` with a non-empty `API_AUTH_KEY`.
- Keep rate limiting enabled unless a stronger upstream limit is guaranteed.
- Use `BRIDGE_API_KEY` for bridge/runtime adapter auth instead of forwarding Binance account secrets.
- Keep `BINANCE_API_KEY` and `BINANCE_API_SECRET` limited to flows that truly need account-backed access.
- Never commit `.env`, live payload files, or secrets.

## Runtime behavior
- Treat `APP_MODE=mock` as a development convenience only.
- Treat `APP_MODE=live` as invalid outside development if `BINANCE_SKILLS_BASE_URL` is missing.
- Prefer dry-run modes for Square publishing until credentials and content flow are verified.
- Fail soft in analysis output when live payloads are partial, but fail fast on missing production auth/config.

## Data handling
- Normalize raw payloads before analysis.
- Keep risk and data-quality warnings visible in rendered output.
- Avoid trusting redirects or unconstrained file paths in live adapters.

## Operating model
- Bibipilot is a research and publishing system, not an autonomous trading engine.
- New execution features should remain isolated from the current analysis and publishing paths.
