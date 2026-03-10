# Product Requirements Document (PRD)

# Bibipilot

**Short name:** Bibipilot  
**Tagline:** Less noise. Better conviction.

## 1. Product Summary
Bibipilot is a research-first AI copilot built on OpenClaw and Binance Skills Hub. It helps users move from fragmented token, wallet, meme, and smart-money data to a concise decision-support brief.

The product is designed to answer a simple question:

**Is this token, wallet, signal, or narrative actually worth attention?**

It does this by combining Binance Skills outputs into a structured response focused on signal quality, risks, context, and what to watch next.

## 2. Problem
Crypto research is fragmented and noisy.

Users jump across:
- token search tools
- market dashboards
- wallet trackers
- smart-money feeds
- meme launchpad screens
- audit/scam checkers
- social narrative trackers

This creates two problems:
1. too much raw information
2. not enough interpretation

Most tools show movement. Fewer help users judge whether the movement deserves conviction.

## 3. Vision
Build the best Binance Skills-powered **signal-and-risk research copilot**.

Bibipilot should:
- reduce noise
- improve conviction
- surface risk clearly
- stay research-first
- produce shareable output to Binance Square

## 4. Product Goals
### Primary goals
- Turn raw Binance Skills outputs into clear research briefs
- Help users evaluate tokens, wallets, signals, and market narratives faster
- Make Binance Square posting a core product output
- Keep the product safe, cautious, and human-supervised

### Secondary goals
- Enable richer daily market summaries
- Improve meme/narrative discovery
- support future saved views, watchlists, and reports

### Non-goals for MVP
- fully autonomous trading
- hidden execution logic
- promising profits or safety
- replacing user judgment

## 5. Target Users
### Primary users
- retail crypto researchers
- active Binance / Binance Web3 users
- on-chain traders looking for signal + risk context
- users who want fast market summaries and Square-ready output

### Secondary users
- content creators posting research to Binance Square
- users tracking meme launches, smart money, and narratives
- advanced users who may later want gated spot integration

## 6. Core Product Principles
- **Research first** — prioritize analysis over execution
- **Risk visible by default** — do not hide or soften major risks
- **No fake certainty** — low risk is not equal to safe
- **Skills-first integration** — use Binance Skills/runtime as the primary capability model
- **Human supervised** — any future execution must stay gated
- **Publishable output** — every strong brief should be convertible into a Square-ready post

## 7. Core User Jobs
Users should be able to ask:
- What do I need to know about this token?
- Is this signal strong or weak?
- What are the main risks here?
- What is smart money doing?
- What wallets or narratives are worth attention today?
- Is this meme token early, crowded, or suspicious?
- Turn this insight into a Binance Square post.

## 8. Core Skills Model
### Research core
- `query-token-info`
- `query-token-audit`
- `query-address-info`
- `crypto-market-rank`
- `meme-rush`
- `trading-signal`

### Required output skill
- `square-post`

### Deferred higher-risk execution skill
- `spot`

## 9. Main Product Surfaces
### A. `/token <symbol>`
Purpose:
- provide a concise token brief

Inputs:
- token info
- market rank context
- trading signal
- token audit

Output:
- Quick Verdict
- Signal Quality
- Top Risks
- Why It Matters
- What To Watch Next
- Risk Tags
- Conviction

### B. `/wallet <address>`
Purpose:
- interpret wallet holdings and posture

Inputs:
- wallet holdings
- optional token enrichment
- optional trader/market context

Output:
- wallet behavior summary
- concentration context
- exposures
- major risks
- what to watch next

### C. `/watchtoday`
Purpose:
- summarize what matters today

Inputs:
- crypto-market-rank
- meme-rush
- trading-signal

Output:
- top narratives
- strongest signals
- smart-money context
- main risk zones
- market takeaway

### D. `/signal <token>`
Purpose:
- evaluate whether a signal deserves attention

Inputs:
- trading-signal
- token info
- token audit

Output:
- signal status
- signal quality
- fragility / confirmation conditions
- risk context
- what to watch next

### E. Binance Square output
Purpose:
- convert insight into a public-ready short post

Inputs:
- research brief
- Square post formatting rules

Output:
- concise Binance Square-ready post
- publish path via `square-post`

## 10. Detailed Skill Roles
### `query-token-info`
Provides:
- token search
- metadata
- creator/project context
- social links
- real-time dynamic market data
- K-Line data

### `query-token-audit`
Provides:
- security scan
- trade/scam/contract risk categories
- buy/sell tax
- verification status

Important rule:
Audit output is only valid when:
- `hasResult=true`
- `isSupported=true`

### `query-address-info`
Provides:
- wallet holdings
- quantities
- token-level price and 24h change
- portfolio inventory basis

### `crypto-market-rank`
Provides:
- trending / top search / alpha / stock discovery
- social hype leaderboard
- smart money inflow ranking
- meme rank
- trader/KOL pnl leaderboard

### `meme-rush`
Provides:
- new/finalizing/migrated meme lifecycle data
- holder-distribution risk
- dev behavior / wash-trading filters
- topic rush / narrative inflow intelligence

### `trading-signal`
Provides:
- smart-money buy/sell signals
- signal timing and direction
- alert/current price comparison
- max gain
- exit rate
- active vs timeout vs completed context

### `square-post`
Provides:
- required publishing/output path for concise public summaries

### `spot`
Provides later:
- public spot market data
- account reads
- order placement and execution

This must remain deferred and strongly gated.

## 11. Output Specification
### Standard brief sections
- Quick Verdict
- Signal Quality
- Top Risks
- Why It Matters
- What To Watch Next
- Risk Tags (when applicable)
- Conviction
- Beginner Note (when useful)

### Tone requirements
- concise
- direct
- caution-aware
- no hype language without evidence
- no investment advice framing

## 12. Binance Square Requirements
Square output is a **must-have** capability.

Requirements:
- post text must be concise and readable
- should preserve risk-aware framing
- should avoid overclaiming certainty
- should support dry-run/draft flow
- should return published post URL on success when available

## 13. Safety Requirements
### Required safety behavior
- never call a token “safe” based solely on audit output
- low risk does not equal safe
- audit is point-in-time only
- do not provide investment advice from audit checks
- execution features must require explicit confirmation
- mainnet trading should require a clear confirmation step

### `spot` safety policy
- keep disabled or deferred by default
- separate read mode from trade mode
- require explicit human confirmation for mainnet execution
- prefer testnet first
- never auto-trade silently

## 14. Functional Requirements
### Must-have
- runnable token / wallet / signal / watchtoday flows
- normalized data contracts
- analyzers and formatters
- Binance Square draft/publish path
- clear docs and release notes
- tests for core scaffolding

### Should-have
- better fallback handling when live skill data is partial
- better validation against live skill schemas
- improved examples and screenshots

### Nice-to-have
- watchlists
- scheduled digests
- saved research reports
- richer API/auth controls
- optional web UI

## 15. Success Metrics
### Product quality
- user can get a useful token brief in one turn
- user can generate a Square-ready post from a brief
- outputs remain risk-aware and structured

### Technical quality
- compile checks pass
- test suite passes
- live adapter path works with real runtime outputs
- Square post succeeds with valid credentials

### Product fit
- users understand not only what is moving, but whether it is worth attention

## 16. Current State
The project is currently:
- a strong scaffold
- well positioned
- increasingly aligned to real Binance Skills
- capable of mock/demo usage now
- partially wired for live-mode repo-side behavior

Still remaining for full live readiness:
- real Binance Skills runtime invocation in production flow
- real payload validation against live outputs
- final deployment hardening
- final end-to-end verification

## 17. Roadmap Summary
### Phase 1
- strong research MVP
- token / wallet / signal / watchtoday briefs
- Square-ready output

### Phase 2
- live Binance Skills alignment
- validate schemas and field mappings
- improve fallback and real-data heuristics

### Phase 3
- product polish
- screenshots/demo package
- richer user modes

### Phase 4
- carefully gated `spot` read/execution options
- watchlists and persistent reports
- web/app expansion if needed

## 18. Final Positioning
Bibipilot is not just another crypto assistant.

It is a **signal-and-risk research copilot** that turns Binance Skills outputs into clearer conviction — and then turns good insight into a Binance Square-ready post.
