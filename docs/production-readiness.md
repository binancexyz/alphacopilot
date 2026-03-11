# Production Readiness

This repo is now closer to production in terms of structure, but real production deployment still requires upstream runtime access and operational setup.

## What is production-ready inside the repo
- stable Python CLI commands
- analyzer/formatter pipeline
- file-based and HTTP-based live adapter loading
- FastAPI surface for serving briefs
- test coverage for adapter loading and API endpoints
- docs for live mode and runtime handoff

## Run the API locally
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make api
```

Endpoints:
- `GET /health`
- `GET /runtime/report`
- `GET /brief/token?symbol=BNB`
- `GET /brief/signal?token=DOGE`
- `GET /brief/wallet?address=0x1234567890ab`
- `GET /brief/watchtoday`

## Mock mode
Default mode for safe demos:
```bash
APP_MODE=mock make api
```

## Live mode
Use either:
- `BINANCE_SKILLS_BASE_URL=file:///absolute/path/to/payloads`
- `BINANCE_SKILLS_BASE_URL=https://adapter.example.com/runtime`

Example:
```bash
APP_MODE=live \
BINANCE_SKILLS_BASE_URL=file:///absolute/path/to/payloads \
make api
```

## Still required before calling it truly production-ready
### Upstream integration
- real OpenClaw runtime command collection
- real Binance Skills Hub invocation
- authenticated adapter service or direct runtime bridge

### Ops/security
- pin deployment environment
- set secrets through a real secret manager
- add request logging/monitoring
- add rate limiting if exposed publicly
- add auth in front of the API if internet-facing
- validate no secrets are committed before release
- monitor `/health` and `/runtime/report` in live mode so runtime state is not confused with product quality

### Product validation
- run against real payloads from upstream
- verify partial-failure fallback messaging
- collect at least one end-to-end live demo capture per command
