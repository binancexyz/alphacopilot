# Current Checklist

A consolidated practical checklist for the current Bibipilot repo state.

## Before stepping away
- [ ] run `make check`
- [ ] run `make test`
- [ ] update docs if behavior changed
- [ ] commit small, clear changes
- [ ] push to GitHub if this is a sharing checkpoint

## Before public sharing / release
### Repo safety
- [ ] run one stronger final secret scan if available
- [ ] confirm `.env` and secrets stay untracked
- [ ] review example payloads for anything private or account-specific
- [ ] confirm public-facing docs do not contain accidental private/workspace-local references

### Product honesty
- [ ] keep README framing accurate for public alpha
- [ ] keep partial runtime/live coverage described honestly
- [ ] avoid describing Bibipilot as an autonomous trading system

### Docs spine
- [ ] README is current
- [ ] install guide is current
- [ ] quick reference is current
- [ ] docs index points to the best entry docs
- [ ] examples reflect current output shape

### Demo / launch assets
- [ ] capture screenshots or short demo clip if needed
- [ ] rehearse demo narration
- [ ] finalize submission/release copy if needed

## Before returning later
- [ ] read `docs/maintainer-summary.md`
- [ ] read `docs/final-summary.md`
- [ ] read `docs/command-architecture.md`
- [ ] decide whether the next work is runtime depth, product refinement, or release polish

## Current truth
Bibipilot is already beyond concept stage.
The main remaining work is now:
- runtime depth
- release hygiene
- demo/public packaging
- iterative product refinement from real usage
