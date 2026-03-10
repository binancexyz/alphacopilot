# Contributor Notes

## Project intent
AlphaCopilot is a signal-and-risk research copilot, not a hype bot and not an auto-profit promise machine.

## Contribution priorities
Best contribution areas:
- live adapter wiring
- normalized payload extraction
- heuristic improvements
- cleaner output formatting
- demo polish
- docs clarity

## What to protect
When making changes, keep these product traits intact:
- concise output
- risk-aware reasoning
- signal over noise
- clear watch-next guidance
- no overconfident claims

## Architecture rule
Keep runtime-specific logic separate from reusable domain logic.
That means:
- OpenClaw handles orchestration
- Python handles interpretation and formatting

## Good changes
- improve clarity
- improve maintainability
- improve normalized contracts
- improve demoability

## Bad changes
- adding hypey language
- making outputs too long and noisy
- hiding risk context
- overcoupling business logic to one runtime
