# Build Checklist

## Immediate priorities

- [x] Add audit hard-gate logic to `/token`
- [x] Add audit hard-gate logic to `/signal`
- [x] Define blocked output state for critical audit failures
- [x] Parse `timeFrame` into signal age labels: `FRESH` / `AGING` / `STALE` (plumbing added; live richness still needs improvement)
- [x] Interpret `exitRate` into early / mixed / late signal posture (first-pass plumbing added)
- [x] Redesign `/watchtoday` into named feed sections
- [x] Add `/audit`
- [x] Add `/meme`
- [ ] Design Square compression templates for public posting
- [ ] Parallelize multi-skill fetches where possible

## Output quality

- [x] Keep `/price` compact and market-card style
- [x] Keep `/brief` ultra-compact
- [x] Keep `/risk` downside-first
- [x] Keep `/token` token-specific, not generic
- [x] Keep `/signal` tactical and freshness-aware (first-pass live support)
- [x] Keep `/wallet` judgment-heavy
- [x] Keep `/watchtoday` feed-structured and prioritization-first

## Product framing

- [x] Present Bibipilot as research -> judgment -> publishing
- [x] Map each major output section to a real Binance Skill
- [x] Make audit gating a visible product strength in demos and submission copy

## Current best next work

- [ ] Improve richer live runtime coverage and bridge stability
- [ ] Strengthen wallet evidence behind follow verdicts
- [ ] Strengthen `/meme` with richer live lifecycle data
- [ ] Add Square compression templates for public posting
- [ ] Trim/curate public docs for a cleaner open-source first impression
