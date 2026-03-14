# `/wallet` Heuristics

## Goal
Interpret wallet behavior, not just balances.

## Inputs
Use `WalletContext`:
- address
- portfolio_value
- holdings_count
- top_holdings
- top_concentration_pct
- change_24h
- notable_exposures
- major_risks

## Signal Quality Rules
### Medium
Use **Medium** when the wallet provides meaningful concentration or behavior signal worth monitoring.

### Low
Use **Low** when the wallet context is shallow, unclear, or too incomplete.

## Key idea
A large wallet is not automatically smart money.
The real value is in:
- concentration patterns
- exposure type
- rotation behavior
- consistency over time
