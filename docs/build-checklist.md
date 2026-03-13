# Build Checklist

## Immediate priorities

- [x] Add audit hard-gate logic to deeper asset judgment
- [x] Add audit hard-gate logic to `/signal`
- [x] Define blocked output state for critical audit failures
- [x] Parse `timeFrame` into signal age labels: `FRESH` / `AGING` / `STALE` (plumbing added; live richness still needs improvement)
- [x] Interpret `exitRate` into early / mixed / late signal posture (first-pass plumbing added)
- [x] Redesign `/watchtoday` into named feed sections
- [x] Add `/audit`
- [ ] Design Square compression templates for public posting
- [ ] Parallelize multi-skill fetches where possible

## Output quality

- [x] Keep `/brief` ultra-compact
- [x] Keep `/brief ... deep` judgment-heavy
- [x] Keep `/signal` tactical and freshness-aware (first-pass live support)
- [x] Keep `/holdings` posture/judgment-heavy
- [x] Keep `/watchtoday` feed-structured and prioritization-first

## Product framing

- [x] Present Bibipilot as research -> judgment -> publishing
- [x] Map each major output section to a real Binance Skill
- [x] Make audit gating a visible product strength in demos and submission copy

## Current best next work

- [ ] Improve richer live runtime coverage and bridge stability
- [ ] Strengthen ownership/wallet evidence behind holdings behavior reads
- [ ] Improve richer caution/lifecycle context where it strengthens `/audit`
- [ ] Add Square compression templates for public posting
- [ ] Trim/curate public docs for a cleaner open-source first impression
