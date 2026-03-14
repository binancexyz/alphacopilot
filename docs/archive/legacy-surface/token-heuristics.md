# `/token` Heuristics

This document defines the first-pass heuristic rules for the live `/token` command.

## Goal
Turn normalized token context into a concise research brief without pretending false precision.

## Inputs
Use the normalized `TokenContext` fields:
- symbol
- price
- liquidity
- holders
- market_rank_context
- signal_status
- signal_trigger_context
- audit_flags
- major_risks

## Signal Quality Rules
### High
Use **High** when most of these are true:
- token has meaningful liquidity
- token has clear holder/activity footprint
- signal status suggests active or constructive context
- no obvious audit flags

### Medium
Use **Medium** when:
- there is some useful signal context
- but confirmation is incomplete
- or some risk context still reduces confidence

### Low
Use **Low** when:
- signal context is weak or missing
- risk context outweighs positive signal
- audit or structural concerns are significant

## Conviction Rules
### High conviction
- high signal quality
- low number of major risks
- no meaningful audit flags

### Medium conviction
- medium signal quality
- manageable risk count
- still worth monitoring

### Low conviction
- weak signal quality
- elevated risk
- multiple audit or structural concerns

## Risk Tag Rules
### Narrative Risk
Add when:
- signal depends strongly on attention
- market rank context suggests trend sensitivity

### Liquidity Risk
Add when:
- liquidity is weak
- or token context is too thin for confidence

### Contract Risk
Add when:
- audit flags exist

## Quick Verdict Pattern
Good quick verdicts should sound like:
- "Looks worth monitoring, but conviction still depends on confirmation and risk balance."
- "Interesting signal context, but structural risk still limits confidence."
- "Signal is visible, though fragility remains elevated."

Avoid:
- moon language
- guaranteed language
- over-precise predictions
