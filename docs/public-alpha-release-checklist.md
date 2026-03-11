# Public Alpha Release Checklist

This checklist is for making Bibipilot safe and clear as an open-source public alpha.

---

## Must fix before public release

### Repo safety
- [ ] Confirm `.env` is ignored and not committed
- [ ] Confirm `.env.example` contains placeholders only
- [ ] Run one final broad secret scan before flipping visibility
- [ ] Review tracked example payloads for anything private or account-specific
- [ ] Review tracked docs for any private notes or personal references

### Public clarity
- [x] Rewrite README so it reflects the current product and command surface
- [ ] Confirm README examples all still work
- [ ] Clearly label the repo as **public alpha**
- [ ] Make mock mode vs live mode behavior explicit
- [ ] Make current live coverage vs partial coverage explicit

### Public docs spine
Keep a clean first path for strangers:
- [ ] README
- [ ] install guide
- [ ] quick reference
- [ ] docs index
- [ ] contribution guide
- [ ] security guide

### Product honesty
- [ ] Avoid describing Bibipilot as a finished autonomous trading system
- [ ] Keep language around live coverage accurate
- [ ] Keep unfinished branches framed as roadmap, not current capability

---

## Should fix before public release

### Repo hygiene
- [ ] Review whether `agent/AGENTS.md`, `agent/IDENTITY.md`, and `agent/SOUL.md` should remain public
- [ ] Archive, trim, or deprioritize stale/internal docs
- [ ] Reduce duplicate docs where possible
- [ ] Make the docs index point clearly to the best current docs

### Public polish
- [ ] Add one or two screenshots to the README
- [ ] Add a short architecture graphic later if helpful
- [ ] Add a short "What works today" section if README still feels too dense
- [ ] Add a short "What is still partial" section if needed

### Release confidence
- [ ] Run tests/checks one final time before opening the repo broadly
- [ ] Confirm the latest public docs match the current code and command surface
- [ ] Confirm no accidental workspace-local references remain in public-facing docs unless intentional

---

## Safe to leave for later

### Nice-to-have
- [ ] richer `/meme` live lifecycle data
- [ ] richer wallet live runtime data
- [ ] stronger Square compression templates
- [ ] more complete runtime coverage
- [ ] short demo video
- [ ] 5-slide deck asset

These do not block public alpha status as long as the repo is honest about what is partial.

---

## Recommended public framing

Use language like:

> Bibipilot is a public alpha Binance-native research copilot built around a research -> judgment -> publishing workflow.

Avoid language like:

> fully autonomous crypto trading agent

---

## Final release decision rule

Bibipilot is ready to go public when:
- the repo is safe
- the README is accurate
- the docs are understandable
- the product is framed honestly

The goal is not perfection.
The goal is a **credible public alpha**.
