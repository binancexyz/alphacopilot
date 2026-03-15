# Deployment

## Docker
```bash
docker build -t bibipilot .
docker run --rm -p 8000:8000 \
  -e APP_ENV=production \
  -e APP_MODE=live \
  -e BINANCE_SKILLS_BASE_URL=https://adapter.example.com/runtime \
  -e BRIDGE_API_KEY=replace-me \
  -e API_AUTH_ENABLED=true \
  -e API_AUTH_KEY=replace-me \
  bibipilot
```

Container runs as a non-root `appuser` on port `8000`.

## Local process
```bash
source .venv/bin/activate
APP_ENV=production API_AUTH_ENABLED=true API_AUTH_KEY=replace-me make api
```

## Bridge API
```bash
source .venv/bin/activate
APP_ENV=production BRIDGE_LIVE_ENABLED=true BRIDGE_API_KEY=replace-me make bridge-api
```

Use the bridge when OpenClaw or another runtime needs raw bundle access instead of rendered briefs.

## Required production controls
- Set `APP_ENV=production`.
- Enable `API_AUTH_ENABLED=true` and provide `API_AUTH_KEY`.
- Keep `API_RATE_LIMIT_ENABLED=true` unless a stronger upstream limiter is in place.
- Set `BINANCE_SKILLS_BASE_URL` for `APP_MODE=live`.
- Set `BRIDGE_API_KEY` if the runtime adapter or bridge is reachable outside a private network.
- Keep secrets in environment variables or a secret manager.

## Health checks
```bash
curl -H 'X-API-Key: replace-me' http://127.0.0.1:8000/health
curl -H 'X-API-Key: replace-me' 'http://127.0.0.1:8010/runtime?command=token&entity=BNB'
```

In locked-down environments the apps fail fast on startup when required auth or live-runtime settings are missing.
