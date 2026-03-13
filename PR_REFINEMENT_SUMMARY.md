# Refine thin-state rendering and judgment quality across Bibipilot

## Overview

This PR improves Bibipilot in two ways:

1. **Thin/degraded runtime outputs now stay structured and readable**
2. **Judgment quality is sharper in key commands**

The focus is not feature expansion.  
The focus is making Bibipilot feel **more trustworthy, more premium, and less fragile** when runtime context is imperfect.

---

## Why

Before this pass, several outputs had the same recurring weaknesses:

- thin live payloads could make cards feel collapsed or placeholder-heavy
- degraded runtime states surfaced too much technical clutter
- different signal/audit/token conditions could collapse into overly generic verdicts
- some sections disappeared or drifted visually under weak payloads

This PR addresses those product-quality problems directly.

---

## Scope

### Thin/degraded output hardening
Improved compact-card stability across:

- `/brief`
- `/brief deep`
- `/signal`
- `/watchtoday`
- `/audit`
- `/holdings`

Key improvements:
- cards keep their intended shape
- placeholders render intentionally
- thin cases avoid sloppy fallback prose
- degraded states remain readable and compact

---

### Runtime footer cleanup
Normalized degraded/runtime warnings into shorter product-style labels.

Examples:
- `Runtime dependency missing`
- `Live bridge limited`
- `Limited audit visibility`

This keeps trust signals visible without polluting compact outputs.

---

### `/signal` judgment refinement
Upgraded signal evaluation from generic buckets into clearer setup states.

Signal outcomes now distinguish:
- blocked
- unmatched
- thin
- stale
- early
- active
- late

Judgment now uses:
- trigger vs current price
- smart-money count
- freshness / age
- exit pressure
- audit gate / flags

Result:
- fewer generic “watchlist only” reads
- more honest setup-state labeling

---

### `/audit` judgment refinement
Made audit analysis more explicit about severity and validity.

Improvements:
- clearer Contract / Liquidity / Structure findings
- stricter unsupported/no-result handling
- better blocked vs warned vs limited separation
- tax-heavy cases surfaced differently from structural danger

Examples:
- `Avoid. Structural risk is too high.`
- `Tradable but flagged. Tax friction is high.`
- `Limited audit visibility. Stay cautious.`

---

### `/brief deep` judgment refinement
Turned `/brief deep` into a more synthesized asset judgment card.

It now weighs:
- audit gate
- evidence depth
- signal match quality
- timing freshness
- exit pressure
- ownership concentration
- liquidity quality
- smart-money presence

This improves verdict quality and better aligns the visible snapshot with the actual judgment.

---

### `/holdings` unavailable/thin-state polish
Improved unavailable-state behavior so holdings cards still feel like product output.

Changes:
- sections stay visible
- placeholders look intentional
- footer context is clearer
- unavailable states no longer feel like dead-end errors

---

### Final thin-copy polish
Final pass focused on wording only.

Examples:
- `No clear entry` → `Signal not confirmed`
- thin trend language → `Limited read`
- `/watchtoday` thin placeholders now read more naturally

---

## Testing

Added and updated tests for:

- thin payload rendering
- rendered consistency
- holdings thin/unavailable states
- runtime footer cleanup
- signal judgment states
- audit judgment states
- token judgment states
- token render alignment
- thin-copy polish

Also performed rendered sanity checks across:
- `/brief`
- `/brief deep`
- `/signal`
- `/watchtoday`
- `/audit`
- `/holdings`

---

## Commits in this pass

- `1b40d4d` Keep compact cards stable on thin payloads
- `3450570` Polish thin-state card wording
- `ecf0652` Tighten rendered card consistency
- `c992c5f` Improve holdings thin-state cards
- `30f5ce6` Unify degraded runtime footer wording
- `f88caee` Refine signal judgment states
- `45c11b1` Refine audit judgment states
- `028ea48` Refine token judgment states
- `93d7055` Polish thin-state output copy

---

## Net effect

This PR does not add major new features.

It does:
- improve trust under degraded runtime conditions
- sharpen judgment in the highest-value commands
- reduce noisy presentation
- make Bibipilot feel more intentional overall

---

## Recommended next step

After merge, the best follow-up is:

- run real live commands/endpoints
- collect weak outputs
- do a smaller evidence-based refinement pass from actual usage
