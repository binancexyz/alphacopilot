# Deep Check - Bibipilot

> Historical review note: this document captures an earlier audit pass during the transition from a wider command surface toward the newer canonical five-command map. Treat it as diagnostic history, not the latest product surface reference.


## Goal
A focused product/code audit of the current Bibipilot surface with emphasis on:
- command quality
- output quality
- trust framing
- consistency
- near-term enhancement opportunities

## Summary
Bibipilot has moved past the concept stage. The strongest product value is now in:
- cleaner judgment
- more premium output presentation
- stronger source/context framing
- selective refinement instead of feature expansion

The best current surfaces are:
- `/portfolio`
- `/watchtoday`
- `/token`
- `/signal`

The weaker surfaces were the compact cards:
- `/price`
- `/brief`
- `/risk`
- `/audit`

These were upgraded in the current pass to better match the product's premium slash-output direction.

## Improvements shipped in this pass

### 1. Safer CLI startup
`src/main.py` now lazy-imports `careers_tracker` only when `careers` is invoked.

Why it matters:
- unrelated commands no longer fail early just because optional careers dependencies are missing
- CLI behavior is more robust and modular

### 2. Premium formatting pass for weaker commands
Improved formatter output for:
- `/price`
- `/brief`
- `/risk`
- `/audit`

Changes:
- stronger tree-style hierarchy
- clearer section separation
- less flat text output
- better alignment with `/portfolio`, `/watchtoday`, `/token`, and `/signal`

### 3. Cleaner source wording
Removed user-facing CoinGecko-specific fallback wording.

Current behavior:
- non-primary quote paths now surface as `Secondary market data`
- user-facing output avoids internal implementation leakage

## Feature-by-feature read

### `/price`
Strengths:
- fast market truth
- useful ranking and volume context
- can surface source context

Needs more work:
- still more utility-like than judgment-like
- could show execution context more elegantly when Binance Spot is active

Best next step:
- add optional pair/spread section when Binance Spot is the active source

### `/brief`
Strengths:
- best candidate for default command
- combines price, signal, and liquidity into a fast read

Needs more work:
- wording can still become repetitive
- source context should feel even more natural and less fallback-oriented

Best next step:
- tighten confidence vocabulary so `watch`, `provisional`, `constructive`, and `usable` each have cleaner meaning

### `/token`
Strengths:
- strong overall command shape
- good integration of setup, risk, tags, and posture

Needs more work:
- repeated phrases around missing/thin/unmatched evidence

Best next step:
- centralize conviction language rules in shared helpers

### `/signal`
Strengths:
- clear setup fragility framing
- good watch/risk structure

Needs more work:
- should become sharper on invalidation and timing

Best next step:
- add explicit invalidation language (`breaks if`, `watch for failure if`)

### `/risk`
Strengths:
- useful downside-first framing
- good fit for posture-aware analysis

Needs more work:
- should separate structural risk, market risk, and posture risk more clearly

Best next step:
- migrate quote sourcing to a more consistent shared market-quote path if needed

### `/audit`
Strengths:
- clear gate concept
- good safety-first role

Needs more work:
- should distinguish stronger between full-valid audit results and limited audit visibility

Best next step:
- improve unsupported/partial-result handling presentation

### `/watchtoday`
Strengths:
- now much stronger visually
- useful market board shape
- posture-aware context adds differentiation

Needs more work:
- sparse or weaker lanes should be omitted more aggressively
- hardcoded exchange-board fallback could be smarter over time

Best next step:
- improve lane confidence thresholds and selective omission

### `/wallet`
Strengths:
- good posture concept
- differentiated from `/portfolio`

Needs more work:
- behavior interpretation can become more distinctive

Best next step:
- add wallet style/archetype labels

### `/portfolio`
Strengths:
- one of the strongest surfaces in the product
- history, drift, and grouped exposure make it feel premium

Needs more work:
- freshness/time context can become clearer
- biggest-change summaries can become more prominent

Best next step:
- add snapshot freshness and stronger drift storytelling

### `/meme`
Strengths:
- useful niche surface
- good fit for hype-vs-quality filtering

Needs more work:
- should push caution/trust framing harder than a standard token command

Best next step:
- make participation-quality judgment more explicit

### `careers`
Strengths:
- useful ecosystem context lane

Needs more work:
- should remain intentionally lightweight

Best next step:
- keep deprioritized relative to core market/posture/publishing surfaces

## Cross-cutting priorities

### Output consistency
Not all commands yet feel equally premium.

Priority:
- continue standardizing section layout, tag presentation, and tree hierarchy across the main command family

### Controlled language
Some judgment phrases repeat too often.

Priority:
- build a small shared vocabulary for confidence, fragility, and evidence quality states

### Trust framing
Source and fallback transparency is improving, but can still be more uniform.

Priority:
- use a consistent `Context` or `Source` section/tag pattern where relevant

### Selectivity over verbosity
The product is better when it says less but says it more clearly.

Priority:
- omit weak or low-value sections instead of filling space

## Recommended command-surface direction
A cleaner product story is now available:

### Core commands
- `/brief`
- `/token`
- `/signal`
- `/portfolio`
- `/wallet`
- `/watchtoday`

### Specialist commands
- `/price`
- `/risk`
- `/audit`
- `/meme`
- `careers`

Why this matters:
- less overlap
- better onboarding
- cleaner demos
- stronger product identity

## Current conclusion
The right move remains refinement over expansion.
Bibipilot already has a real product shape.
The highest-value path now is:
- sharper outputs
- cleaner confidence language
- stronger trust framing
- better consistency across the command surface
- clearer presentation of core vs specialist commands
