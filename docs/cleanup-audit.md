# Cleanup Audit

## Goal
Reduce docs/repo noise without deleting useful knowledge blindly.

This audit groups files into:
- keep
- merge candidate
- archive candidate
- delete candidate (only after human review)

## Current shape
- `docs/` top-level files: 125
- `examples/` files: 10

That is enough volume that repo clarity is now a maintenance problem, not just a style problem.

---

## Keep
These are strong current-truth or onboarding files and should remain easy to find.

### Product truth / onboarding
- `README.md`
- `docs/INDEX.md`
- `docs/prd.md`
- `docs/architecture.md`
- `docs/commands-overview.md`
- `docs/command-architecture.md`
- `docs/quick-reference.md`
- `docs/one-minute-overview.md`
- `docs/maintainer-summary.md`
- `docs/final-summary.md`
- `docs/final-status.md`
- `docs/final-hand-off.md`
- `docs/example-usage.md`
- `examples/current-output-examples.md`
- `examples/README.md`

### Core implementation / runtime docs
- `docs/binance-skills-architecture-summary.md`
- `docs/binance-spot-integration.md`
- `docs/openclaw-runtime-integration.md`
- `docs/openclaw-runtime-bridge.md`
- `docs/live-bridge-spec.md`
- `docs/live-command-mapping.md`
- `docs/normalized-data-contracts.md`
- `docs/token-live-design.md`
- `docs/signal-live-design.md`
- `docs/wallet-live-design.md`
- `docs/watchtoday-live-design.md`

### Core quality / policy docs
- `docs/output-policy.md`
- `docs/security-principles.md`
- `docs/deployment.md`
- `docs/install.md`
- `docs/production-readiness.md`

---

## Merge candidates
These are useful, but likely too fragmented.
They should probably be merged into a smaller set of stronger reference docs.

### Demo cluster
Likely merge into:
- `docs/demo-script.md`
- `docs/demo-checklist.md`
- `docs/live-proof-appendix.md`

Current fragmented files:
- `docs/demo-assets-plan.md`
- `docs/demo-operator-sheet.md`
- `docs/final-demo-narration.md`
- `docs/runtime-demo.md`
- `docs/spoken-pitch-pack.md`

### Submission/release cluster
Likely merge into a smaller release/submission pack.

Current overlapping files:
- `docs/submission.md`
- `docs/submission-short.md`
- `docs/submission-medium.md`
- `docs/public-release-message.md`
- `docs/release-notes-draft.md`
- `docs/launch-package.md`
- `docs/quote-posts.md`
- `docs/final-x-posts.md`

### Checklist cluster
Too many list-shaped docs with overlapping function.
Likely merge into one or two operational checklists.

Current overlapping files:
- `docs/build-checklist.md`
- `docs/demo-checklist.md`
- `docs/first-session-checklist.md`
- `docs/live-integration-checklist.md`
- `docs/maintainer-checklist.md`
- `docs/release-checklist.md`
- `docs/final-release-checklist.md`
- `docs/public-alpha-release-checklist.md`
- `docs/public-repo-checklist.md`
- `docs/review-checklist.md`

### Final-summary cluster
A lot of “final-*” files are snapshots of moments, not durable references.
Likely merge the important bits into:
- `docs/final-summary.md`
- `docs/final-status.md`
- `docs/final-hand-off.md`

Current overlapping files:
- `docs/final-engineering-note.md`
- `docs/final-next-steps.md`
- `docs/final-public-release-check.md`
- `docs/final-remaining-work-tracker.md`
- `docs/final-repo-polish.md`

---

## Archive candidates
These may still be useful historically, but they probably should not live at the top level forever.
Best destination would be something like `docs/archive/`.

### Early planning / transitional notes
- `docs/first-real-build.md`
- `docs/implementation-sequence.md`
- `docs/integration-plan.md`
- `docs/live-bridge-implementation-plan.md`
- `docs/runtime-phase-boundary.md`
- `docs/runtime-decision.md`
- `docs/runtime-implementation-notes.md`
- `docs/road-to-live.md`
- `docs/next-questions.md`
- `docs/command-upgrade-order.md`
- `docs/output-evolution-plan.md`

### Low-signal process notes
- `docs/code-quality-notes.md`
- `docs/regression-notes.md`
- `docs/live-data-notes.md`
- `docs/security-notes.md`
- `docs/contributor-notes.md`

### Repo/admin snippets
- `docs/repo-badges.md`
- `docs/repo-description.md`
- `docs/repo-topics.md`
- `docs/github-push.md`
- `docs/git-setup.md`

---

## Delete candidates
Do **not** delete automatically.
These are just the files most likely to be removable after review because they look superseded, tiny, or merged into better docs.

- `docs/public-readme-todo.md`
- `docs/public-repo-checklist.md`
- `docs/review-checklist.md`
- `docs/release-prep.md`
- `docs/release-notes-draft.md`
- `docs/road-to-live.md`
- `docs/quality-bar.md`
- `docs/versioning.md`
- `docs/why-this-project.md`

These are not necessarily bad files; they just look easiest to retire if the goal is a cleaner repo.

---

## Recommended cleanup order

### 1. Safe structural cleanup
- create `docs/archive/`
- move archive candidates there
- keep filenames intact for easy recovery

### 2. Merge high-overlap docs
Start with:
- checklist cluster
- final-summary cluster
- demo cluster

### 3. Remove only after merge/archival is stable
Delete candidates should only be removed after:
- top-level docs index is updated
- no current doc links depend on them
- maintainer agrees the information is redundant

---

## Best immediate action
If cleanup starts now, the safest useful move is:
1. create `docs/archive/`
2. move archive candidates there
3. update `docs/INDEX.md` so current docs stay obvious

That would reduce top-level clutter a lot without destroying information.

---

## Human-review note
Because deletions are destructive, this audit should be treated as a decision aid, not an automatic delete list.
