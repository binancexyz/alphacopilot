# Deployment

## Option 1: Docker (recommended)
```bash
docker build -t bibipilot .
docker run --rm -p 8000:8000 \
  -e APP_MODE=mock \
  bibipilot
```

For live mode:
```bash
docker run --rm -p 8000:8000 \
  -e APP_MODE=live \
  -e BINANCE_SKILLS_BASE_URL=https://adapter.example.com/runtime \
  -e BINANCE_API_KEY=... \
  -e BINANCE_API_SECRET=... \
  bibipilot
```

Container runs Python 3.12-slim as a non-root `appuser` on port 8000.

## Option 2: Local process
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make api
# or: uvicorn src.api:app --host 0.0.0.0 --port 8000
```

Bibipilot auto-loads local `.env` / `.env.local` values when present, so local API keys and runtime settings do not need to be manually exported every time.

## Option 3: Bridge API (for OpenClaw integration)
```bash
make bridge-api
# or: uvicorn src.bridge_api:app --host 0.0.0.0 --port 8001
```

## Recommended hardening
- Keep secrets in environment variables or a secret manager
- Enable `API_AUTH_ENABLED=true` and set `API_AUTH_KEY` before public exposure
- Keep `API_RATE_LIMIT_ENABLED=true` unless the API is fully private behind another limiter
- Keep `API_REQUEST_LOGGING_ENABLED=true` so request paths and statuses are visible in logs
- Verify live-mode connectivity before demos or launch
- Check `/health` for `config_warnings` before blaming the product layer for deployment mistakes

## API versions
- REST API: v0.2.1 (`src/api.py`)
- Bridge API: v0.2.0 (`src/bridge_api.py`)

## Health check
```bash
curl http://localhost:8000/health
```

Returns system status, version, app mode, and any configuration warnings.
