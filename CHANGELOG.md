# Changelog

## Unreleased
### Added
- scheduled Binance Square content engine, now tightened to a premium 1-post/day mode centered on the nightly diary slot
- lightweight anti-repetition state tracking for recurring Square posting
- performance logging, internal writing-seed capture, and weekly recap generation for the Square content engine
- context-aware nightly topic selection plus diary / builder / market night modes for Square posts

### Improved
- comprehensive documentation overhaul across all docs to reflect actual codebase state
- README.md rewritten with table of contents, full API docs, Docker instructions, architecture overview, and current status
- docs/prd.md expanded to cover all 10 commands, REST API, security, tech stack, and current state
- docs/architecture.md updated to reflect FastAPI, bridge API, security layer, and service architecture
- docs/roadmap.md updated with progress tracking (Phase 1 complete, Phase 2 in progress)
- docs/quick-reference.md updated with all 10 commands, API endpoints, and publishing commands
- docs/commands-overview.md expanded with /risk, /audit, /meme, careers, and usage examples
- docs/one-minute-overview.md rewritten with key numbers and three-step workflow
- docs/install.md updated with Docker option, dependency table, and all CLI commands
- docs/deployment.md updated with bridge API option, health check, and API versions
- docs/project-goals.md updated with current status for each goal
- docs/mvp-definition.md updated with full 10-command surface and all product surfaces
- docs/INDEX.md reorganized with categories and links to all doc files
- CONTRIBUTING.md updated with project structure and security posture
- README, scripts docs, and Binance Square docs updated to match the latest live publish/autopost flow
- Makefile targets updated for the current Square diary slot names
- local ignore rules updated to keep generated `tmp/` artifacts out of git
- project branding updated from AlphaCopilot to Bibipilot across docs, metadata, prompts, and local repo paths

### Fixed
- live `/token BNB` matching across bridge and extractor layers
- token brief risk leakage from unrelated ranked tokens

## 2026-03-10
### Added
- Initial Bibipilot scaffold
- Submission, launch, and demo docs
- Agent identity and operating files
- Python command scaffold for `/token`, `/signal`, `/wallet`, `/watchtoday`
- Mock/live service split
- Normalized data contracts and extractor stubs
- Heuristic-driven live-brief builders for all core commands
- Tests, Makefile, GitHub Actions workflow, and PR template

### Improved
- README and installation guidance
- GitHub/release metadata and checklists
- Maintainer handoff and roadmap docs
