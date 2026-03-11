# Deployment

## Option 1: Docker
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

## Option 2: Local process
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./scripts/start_api.sh
```

## Recommended hardening
- keep secrets in environment variables or a secret manager
- enable `API_AUTH_ENABLED=true` and set `API_AUTH_KEY` before public exposure
- keep `API_RATE_LIMIT_ENABLED=true` unless the API is fully private behind another limiter
- keep `API_REQUEST_LOGGING_ENABLED=true` so request paths and statuses are visible in logs
- verify live-mode connectivity before demos or launch
- check `/health` for `config_warnings` before blaming the product layer for deployment mistakes
