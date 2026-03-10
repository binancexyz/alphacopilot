# `/signal` Heuristics

This document defines the first-pass heuristic rules for the live `/signal` command.

## Goal
Turn normalized signal context into a concise research brief that explains quality, fragility, and what confirms the setup next.

## Inputs
Use the normalized `SignalContext` fields:
- token
- signal_status
- trigger_price
- current_price
- max_gain
- exit_rate
- audit_flags
- supporting_context
- major_risks

## Signal Quality Rules
### High
Use **High** when:
- signal status looks active / triggered / bullish
- audit flags are absent
- supporting context is reasonably strong

### Medium
Use **Medium** when:
- signal status is usable or watch-worthy
- but confirmation is still incomplete
- or risks still limit confidence

### Low
Use **Low** when:
- signal is weak, missing, or unclear
- multiple structural risks remain
- audit flags or fragility dominate the setup

## Risk Tags
### Signal Fragility
Always consider this tag.
Signals are fragile by default until follow-through confirms them.

### Contract Risk
Add when audit flags exist.

### Narrative Risk
Add when the setup appears strongly dependent on attention or short-lived momentum.

## Quick Verdict Pattern
Good quick verdicts:
- "Has a monitor-worthy setup, but the signal remains fragile."
- "Shows relatively strong signal quality, though confirmation and risk still matter."
- "Looks lower-conviction because the signal is weak or the risks remain elevated."
