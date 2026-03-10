# Changelog

## Unreleased
### Added
- scheduled Binance Square content engine with 7 daily slots across diary, education, market, builder, ecosystem, motivation, and night reflection formats
- lightweight anti-repetition state tracking for recurring Square posting
- performance logging, internal writing-seed capture, and weekly recap generation for the Square content engine
- CTA rotation, topic rotation, series labels, and slot-specific voice profiles for Square posts

### Improved
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
