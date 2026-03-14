# Command Architecture

## Live Command Map
Bibipilot now has a single public command story built around **7 commands**.

### Research
- `/brief <symbol>` — fast read, with deeper asset judgment when data supports it
- `/watchtoday` — daily market board
- `/alpha [symbol]` — Binance Alpha board by default, Alpha token detail optionally

### Judgment
- `/signal <symbol>` — setup + risk + invalidation
- `/audit <symbol>` — safety read with meme lens folded into findings/context

### Posture
- `/holdings [address]` — private portfolio posture or external wallet behavior
- `/futures <symbol>` — Binance Futures positioning / leverage posture

---

## What disappeared from the public map
These commands still exist for compatibility or internal utility, but they should not lead the product story.

| Older command | New home |
|---|---|
| `/token` | `/brief` (deeper path) |
| `/portfolio` | `/holdings` |
| `/wallet` | `/holdings <address>` |
| `/risk` | `/signal` |
| `/meme` | `/audit` |
| `/price` | hidden utility |
| `careers` | removed from public product surface |
| `/watch` | removed alias |

---

## Why this is better
- less overlap
- faster learning
- cleaner demos
- stronger product identity
- one canonical name per job

---

## Command roles

### `/brief <symbol>`
The flagship asset command.
- default answer surface
- fast by default
- deeper when richer context is available
- should absorb most old `/token` expectations over time

### `/signal <symbol>`
The setup judgment command.
- conviction
- risk
- invalidation
- timing / fragility

### `/holdings [address]`
The posture command.
- no argument → your private Binance Spot posture
- address argument → public wallet behavior read
- one shared mental model: what is owned, and what does it mean?

### `/watchtoday`
The front-page command.
- live board
- ranking/selectivity
- habit-forming daily surface

### `/audit <symbol>`
The safety command.
- structural safety
- contract / risk posture
- meme participation/lifecycle lens when relevant

---

## Compatibility policy
The old commands are not removed all at once.
They can remain as compatibility paths while the public-facing docs, demos, and help now point to the canonical 5-command map.

That means:
1. public docs stay clean
2. old workflows do not break immediately
3. the product can converge without chaos
