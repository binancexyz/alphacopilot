# Live Mode

This repo now supports a practical local/live adapter path even before direct OpenClaw tool invocation is embedded here.

## Modes

### 1. Mock mode
Default behavior.

```bash
python3 src/main.py token BNB
```

### 2. Live mode via file payloads
Point the app at a directory of raw payload JSON files.

```bash
export APP_MODE=live
export BINANCE_SKILLS_BASE_URL=file:///absolute/path/to/payloads
python3 src/main.py token BNB
```

Supported file patterns:
- `token-bnb.json`
- `signal-doge.json`
- `watchtoday.json`
- `token/bnb.json`
- `signal/doge.json`
- `wallet/0xabc.json`

Each JSON file should match the raw skill-output shapes expected by `src/services/live_extractors.py`.

### 3. Live mode via HTTP adapter
Point the app at an HTTP endpoint that returns raw payload JSON.

```bash
export APP_MODE=live
export BINANCE_SKILLS_BASE_URL=https://adapter.example.com/runtime
python3 src/main.py token BNB
```

The service sends:
- `command=token|signal|wallet|watchtoday`
- `entity=<symbol|address>` when relevant

Optional headers:
- `X-API-Key`
- `X-API-Secret`

The endpoint may return either:
- the raw payload object directly, or
- `{ "raw": { ... } }`

## What this finishes
This completes the repo-side live adapter layer for:
- loading live payloads
- extracting normalized context
- building final briefs through the same analyzer path

## What still remains outside this repo
- actual OpenClaw runtime command parsing
- actual Binance Skills Hub tool execution
- production adapter/deployment wiring
