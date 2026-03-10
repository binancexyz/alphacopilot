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

## Principles
Please keep these intact:
- signal over noise
- concise output
- visible risk context
- calm, credible tone
- reusable Python logic separated from runtime-specific orchestration

## Development checks
Before opening a PR, run:

```bash
make check
make test
```

## Suggested workflow
1. Create a focused branch
2. Keep changes small and understandable
3. Update docs if behavior changes
4. Avoid mixing unrelated concerns in one PR

## If unsure
Prefer simpler changes that make the project clearer, more reliable, or easier to extend.
