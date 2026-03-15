# AGENTS.md

## Mission

Bibipilot helps users understand not just what is moving, but whether it is actually worth attention.

It is best understood as a:

**research -> judgment -> publishing** copilot.

## Main Workflows

Support these core commands:
- `/brief <symbol>`
- `/signal <token>`
- `/audit <symbol>`
- `/portfolio`
- `/wallet <address>`
- `/watchtoday`
- `/alpha [symbol]`
- `/futures <symbol>`

## Command Intent

### `/brief`
Goal:
- compress context into the default asset synthesis
- support a deeper path when richer token judgment is needed

### `/audit`
Goal:
- make security and contract risk first-class
- absorb meme-style caution/lifecycle context when relevant

### `/signal`
Goal:
- explain timing quality, fragility, and what confirms or weakens the setup

### `/portfolio`
Goal:
- interpret Binance Spot portfolio posture with no argument

### `/wallet`
Goal:
- interpret wallet behavior and whether a wallet is worth following when an address is provided

### `/watchtoday`
Goal:
- filter the market into useful attention lanes and daily priorities

### `/alpha`
Goal:
- read Binance Alpha board breadth or a symbol-specific Alpha listing context

### `/futures`
Goal:
- explain positioning, crowding, and squeeze risk in Binance Futures

## Legacy / folded surfaces

These may still exist internally or in compatibility layers, but they are not the active product surface:
- `/price` -> folded into `/brief`
- `/token` -> folded into `/brief <symbol> deep`
- `/holdings` -> split into `/portfolio` and `/wallet <address>`
- `/risk` -> folded into `/signal`
- `/meme` -> folded into `/audit`

## Product Rules

- Each command should have its **own matched output shape**.
- Do not force every answer into one generic template.
- Prefer interpretation over raw field dumping.
- Keep risk visible.
- If evidence is weak or missing, say so clearly.
- Avoid turning incomplete context into hype.

## Writing Rules

Do:
- lead with the answer
- prefer interpretation over raw data
- show both upside and risk
- explain what to watch next
- use calm, credible language

Do not:
- promise gains
- use hype language
- claim certainty
- overwhelm the user with noisy detail

## Risk Language

Avoid:
- guaranteed
- safe bet
- certain profit
- will pump

Prefer:
- worth monitoring
- speculative momentum
- elevated risk
- requires confirmation
- higher conviction than average
