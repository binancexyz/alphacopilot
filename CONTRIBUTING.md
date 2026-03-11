# Contributing to Bibipilot

Thanks for contributing.

## Product intent
Bibipilot is a **signal-and-risk research copilot**.

It is not meant to be:
- a hype bot
- a guaranteed-alpha machine
- a noisy dashboard wrapper

## Priorities
Good contributions usually improve one of these:
- live integration wiring
- normalized payload extraction
- output quality
- heuristic quality
- docs clarity
- demoability
- maintainability
- security posture

## Principles
Please keep these intact:
- signal over noise
- concise output
- visible risk context
- calm, credible tone
- reusable Python logic separated from runtime-specific orchestration
- security by default (auth, validation, safe defaults)

## Development checks
Before opening a PR, run:

```bash
make check
make test
```

## Project structure
- `src/analyzers/` — analysis modules for each command
- `src/services/` — core business logic and integrations
- `src/formatters/` — output formatting
- `src/models/` — data schemas
- `src/utils/` — helper functions
- `src/api.py` — FastAPI REST API (v0.2.1)
- `src/bridge_api.py` — OpenClaw live bridge (v0.2.0)
- `src/main.py` — CLI entry point
- `tests/` — test suite

## Suggested workflow
1. Create a focused branch
2. Keep changes small and understandable
3. Update docs if behavior changes
4. Avoid mixing unrelated concerns in one PR
5. Run `make check && make test` before submitting

## If unsure
Prefer simpler changes that make the project clearer, more reliable, or easier to extend.
