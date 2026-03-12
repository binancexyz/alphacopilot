# Runtime Decision

## Current Recommendation
Use **OpenClaw** as the visible runtime for contest alignment, while keeping the reusable logic in Python.

## Why
This gives the project two advantages at once:
1. Better alignment with the Binance / OpenClaw challenge
2. Easier long-term migration if the runtime changes later

## Practical Split

### OpenClaw handles
- assistant runtime
- messaging surface integration
- command routing
- skill orchestration
- memory / agent behavior

### Python handles
- context synthesis
- signal quality interpretation
- risk tagging
- conviction summaries
- output formatting

## Migration Readiness
If the logic remains in Python modules, the project can later move to:
- FastAPI
- custom Telegram runtime
- PydanticAI
- other orchestration layers

without rewriting the core research logic.
