# Error Handling

## Goal
Fail gracefully without destroying the product experience.

## Rules

### 1. Partial data is acceptable
If one skill fails but others succeed:
- still return a brief
- mention reduced confidence
- explain missing context briefly

### 2. Avoid hard crashes in user-facing flows
If live data is unavailable:
- return a short fallback message
- mention that some data could not be retrieved
- avoid pretending certainty

### 3. Confidence should degrade when data is incomplete
If signal, audit, or market context is missing:
- reduce conviction
- mention missing confirmation
- keep wording cautious

## Suggested fallback language
- "Signal context is incomplete right now, so this view should be treated as lower-confidence."
- "Audit context was unavailable in this pass; risk may be understated."
- "Market ranking data could not be retrieved, so this summary may miss broader context."

## Mock mode behavior
In mock mode:
- always return a complete scaffold brief
- clearly treat it as development/demo behavior internally
