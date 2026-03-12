# Product Requirements Document (PRD)

# Bibipilot

**Short name:** Bibipilot
**Tagline:** Less noise. Better conviction.
**Package version:** 0.1.0 (pyproject.toml)
**API version:** 0.2.1 (src/api.py — versioned independently as the REST surface evolves faster)
**Bridge version:** 0.2.0 (src/bridge_api.py — versioned independently for OpenClaw integration)

---

## 1. Product Summary

Bibipilot is a research-first AI copilot built on OpenClaw and Binance Skills Hub. It helps users move from fragmented token, wallet, meme, and smart-money data to concise decision support and publishable Binance Square output.

The product answers a simple question:

**Is this token, wallet, signal, or narrative actually worth attention?**

It does this by combining Binance Skills outputs into structured responses focused on signal quality, risks, context, and what to watch next — and then turning those insights into publishable Binance Square posts through a premium daily content engine.

---

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
1. Too much raw information
2. Not enough interpretation

Most tools show movement. Fewer help users judge whether the movement deserves conviction.

---

## 3. Vision

Build the best Binance Skills-powered **signal-and-risk research copilot**.

Bibipilot should:
- reduce noise
- improve conviction
- surface risk clearly
- stay research-first
- produce shareable output to Binance Square
- maintain a safe, human-supervised posture

---

## 4. Product Goals

### Primary goals
- Turn raw Binance Skills outputs into clear research briefs
- Help users evaluate tokens, wallets, signals, and market narratives faster
- Make Binance Square posting a core product output
- Prefer one high-standard Binance Square post over high-volume repetitive posting
- Keep the product safe, cautious, and human-supervised
- Provide a security-hardened API for programmatic access

### Secondary goals
- Enable richer daily market summaries
- Improve meme/narrative discovery
- Support future saved views, watchlists, and reports
- Provide ecosystem intelligence through Binance Careers tracking

### Non-goals
- Fully autonomous trading
- Hidden execution logic
- Promising profits or safety
- Replacing user judgment

---

## 5. Target Users

### Primary users
- Retail crypto researchers
- Active Binance / Binance Web3 users
- On-chain traders looking for signal and risk context
- Users who want fast market summaries and Square-ready output

### Secondary users
- Content creators posting research to Binance Square
- Users tracking meme launches, smart money, and narratives
- Advanced users who may later want gated spot integration
- Developers integrating via the REST API

---

## 6. Core Product Principles
- **Research first** — prioritize analysis over execution
- **Risk visible by default** — do not hide or soften major risks
- **No fake certainty** — low risk is not equal to safe
- **Skills-first integration** — use Binance Skills/runtime as the primary capability model
- **Human supervised** — any future execution must stay gated
- **Publishable output** — every strong brief should be convertible into a Square-ready post
- **Security by default** — API auth, rate limiting, SSRF protection, path traversal prevention

---

## 7. Core User Jobs

Users should be able to ask:
- What do I need to know about this token?
- Is this signal strong or weak?
- What are the main risks here?
- What is smart money doing?
- What wallets or narratives are worth attention today?
- Is this meme token early, crowded, or suspicious?
- What is the downside risk for this token?
- Is this token safe from a security/audit perspective?
- What is the current market price and spread?
- What is Binance hiring for? (ecosystem intelligence)
- Turn this insight into a Binance Square post.

---

## 8. Core Skills Model

### Research core
| Skill | Purpose |
|-------|---------|
| `query-token-info` | Token metadata, market data, K-Line |
| `query-token-audit` | Security scan, scam/contract risk |
| `query-address-info` | Wallet holdings and portfolio |
| `trading-signal` | Smart-money buy/sell signals |
| `crypto-market-rank` | Trending, alpha, smart-money inflow |
| `meme-rush` | Meme lifecycle, holder distribution |

### Supporting data (optional)
| Source | Purpose |
|--------|---------|
| Binance Spot API | Read-only price, spread, 24h change |
| CoinMarketCap API | Supplemental market quotes |
| Binance Careers API | Ecosystem hiring data |

### Required output skill
- `square-post`

### Deferred higher-risk execution skill
- `spot`

---

## 9. Main Product Surfaces

### A. `/token <symbol>`
**Purpose:** Provide a concise token brief with conviction assessment.

**Inputs:** token info, market rank, trading signal, token audit, Binance Spot (optional)

**Output:** Quick Verdict, Signal Quality, Top Risks, Why It Matters, What To Watch Next, Risk Tags, Conviction

---

### B. `/signal <token>`
**Purpose:** Evaluate whether a smart-money signal deserves attention.

**Inputs:** trading signal, token info, token audit, Binance Spot (optional)

**Output:** Signal status, signal quality, fragility/confirmation conditions, risk context, what to watch next

---

### C. `/wallet <address>`
**Purpose:** Read public posture from an external wallet and judge whether it is worth following.

**Inputs:** wallet holdings, optional token enrichment, optional trader/market context

**Output:** Wallet behavior summary, concentration context, exposures, major risks, what to watch next

---

### D. `/portfolio`
**Purpose:** Read a user's own Binance Spot posture in a private, read-only way.

**Inputs:** signed Binance API account read, current spot prices, local snapshot history

**Output:** estimated visible portfolio value, top holdings, concentration context, grouped exposure mix, posture drift, major risks, what to watch next

---

### E. `/price <symbol>`
**Purpose:** Show a compact market card with exchange-native data.

**Inputs:** Binance Spot read-only data (preferred), token info fallback

**Output:** Current price, 24h change, bid-ask spread, exchange-pair context

---

### F. `/brief <symbol>`
**Purpose:** Premium default market read with exchange-native grounding.

**Inputs:** token info, trading signal, market context, Binance Spot (optional), current posture context when available

**Output:** Compressed market synthesis with conviction and key risks

---

### G. `/risk <symbol>`
**Purpose:** Downside-first risk assessment.

**Inputs:** token info, audit data, signal context, market data

**Output:** Risk severity, top risk factors, downside scenarios, risk tags

---

### H. `/audit <symbol>`
**Purpose:** Security-first token audit card.

**Inputs:** token audit, token info

**Output:** Security status, scam/vulnerability flags, contract risk assessment, audit verdict

**Important rule:** Audit output is only valid when `hasResult=true` and `isSupported=true`.

---

### I. `/watchtoday`
**Purpose:** Summarize what matters today across the market.

**Alias:** `watch today` is accepted as an alternative.

**Inputs:** crypto-market-rank, meme-rush, trading-signal, Binance Spot (optional), current posture context when available

**Output:** Top narratives, strongest signals, smart-money context, main risk zones, market takeaway

---

### J. `/meme <symbol>`
**Purpose:** First-pass meme token scan.

**Inputs:** meme-rush, token info

**Output:** Meme lifecycle status, holder distribution, launch status, risk assessment

---

### K. `careers`
**Purpose:** Optional Binance ecosystem intelligence through hiring data.

**Inputs:** Binance Careers API

**Output:** Active hiring areas, team growth signals, ecosystem priority context

---

### K. Binance Square output
**Purpose:** Convert insights into public-ready short posts.

**Inputs:** Research brief, Square post formatting rules, market context

**Output:**
- Concise Binance Square-ready post
- Publish path via `square-post`
- Premium scheduled daily post path centered on one strong post per day
- Active scheduled slot: `night-diary` at `21:30` Asia/Phnom_Penh
- Context-aware nightly generation with diary / builder / market mode variation

---

### Portfolio safety rule
- read-only first
- no order placement
- no silent trading logic
- private account data must stay local and human-supervised

---

### L. REST API (v0.2.1)
**Purpose:** Programmatic access to all research briefs.

**Endpoints:**
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | System status, version, config warnings |
| GET | `/runtime/report` | Extended runtime diagnostics |
| GET | `/brief/token?symbol=BNB` | Token analysis brief |
| GET | `/brief/signal?token=DOGE` | Signal validation brief |
| GET | `/brief/audit?symbol=BNB` | Security audit brief |
| GET | `/brief/meme?symbol=DOGE` | Meme token brief |
| GET | `/brief/wallet?address=0x...` | Wallet analysis brief |
| GET | `/brief/watchtoday` | Daily market board |

**Security:** Optional API key auth (HMAC timing-safe), rate limiting, security headers, CORS (disabled by default)

---

### M. OpenClaw Bridge (v0.2.0)
**Purpose:** Live bridge for OpenClaw runtime integration.

**Architecture:** Single generic `/runtime` endpoint dispatches to command-specific skill sets via `command` and `entity` query parameters, rather than separate per-command endpoints.

**Endpoints:**
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Bridge health and mode status |
| GET | `/runtime?command=<cmd>&entity=<val>` | Dispatch to skill set for command |

**Supported commands:** `token`, `signal`, `audit`, `meme`, `wallet`, `watchtoday`

**Configuration:** Controlled via `BRIDGE_LIVE_ENABLED`, `BRIDGE_DEFAULT_CHAIN_ID`, `BRIDGE_HTTP_TIMEOUT_SECONDS`, `BRIDGE_HTTP_RETRIES`, and `BRIDGE_HEALTHCHECK_ENABLED` environment variables.

---

## 10. Detailed Skill Roles

### `query-token-info`
Provides: token search, metadata, creator/project context, social links, real-time market data, K-Line data

### `query-token-audit`
Provides: security scan, trade/scam/contract risk categories, buy/sell tax, verification status

Important rule: Audit output is only valid when `hasResult=true` and `isSupported=true`.

### `query-address-info`
Provides: wallet holdings, quantities, token-level price and 24h change, portfolio inventory basis

### `crypto-market-rank`
Provides: trending / top search / alpha / stock discovery, social hype leaderboard, smart money inflow ranking, meme rank, trader/KOL PnL leaderboard

### `meme-rush`
Provides: new/finalizing/migrated meme lifecycle data, holder-distribution risk, dev behavior / wash-trading filters, topic rush / narrative inflow intelligence

### `trading-signal`
Provides: smart-money buy/sell signals, signal timing and direction, alert/current price comparison, max gain, exit rate, active vs timeout vs completed context

### `square-post`
Provides: required publishing/output path for concise public summaries

### `spot`
Provides later: public spot market data, account reads, order placement and execution

This must remain deferred and strongly gated.

---

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
- Concise
- Direct
- Caution-aware
- No hype language without evidence
- No investment advice framing

---

## 12. Binance Square Requirements

Square output is a **must-have** capability.

Requirements:
- Post text must be concise and readable
- Should preserve risk-aware framing
- Should avoid overclaiming certainty
- Should support dry-run/draft flow
- Should return published post URL on success when available
- Scheduled posting should prioritize one high-standard daily post over repetitive multi-slot volume
- Scheduled post generation should adapt tone between diary / builder / market modes when context supports it
- Anti-repetition state tracking across runs
- Context-aware nightly topic selection weighted toward fresh real work
- Distinct diary / builder / market night modes for less repetitive voice

---

## 13. Safety Requirements

### Required safety behavior
- Never call a token "safe" based solely on audit output
- Low risk does not equal safe
- Audit is point-in-time only
- Do not provide investment advice from audit checks
- Execution features must require explicit confirmation
- Mainnet trading should require a clear confirmation step

### `spot` safety policy
- Keep disabled or deferred by default
- Separate read mode from trade mode
- Require explicit human confirmation for mainnet execution
- Prefer testnet first
- Never auto-trade silently

### API security
- HMAC timing-safe API key comparison
- Rate limiting with configurable window
- Path traversal prevention with `Path.is_relative_to`
- SSRF protection with `follow_redirects=False` and URL scheme validation
- Security headers on all responses
- Non-root container execution

### Configurable security settings
| Variable | Default | Purpose |
|----------|---------|---------|
| `API_AUTH_ENABLED` | `false` | Enable API key authentication |
| `API_AUTH_KEY` | *(empty)* | API key for HMAC comparison |
| `API_AUTH_HEADER` | `X-API-Key` | Header name for API key |
| `API_RATE_LIMIT_ENABLED` | `true` | Enable rate limiting |
| `API_RATE_LIMIT_REQUESTS` | `60` | Max requests per window |
| `API_RATE_LIMIT_WINDOW_SECONDS` | `60` | Rate limit window in seconds |
| `API_REQUEST_LOGGING_ENABLED` | `true` | Enable request logging |

---

## 14. Functional Requirements

### Must-have (implemented)
- Runnable token / wallet / signal / watchtoday / price / brief / risk / audit / meme flows
- Careers ecosystem intelligence
- Normalized data contracts
- Analyzers and formatters
- Binance Square draft/publish path
- Scheduled premium daily posting engine
- FastAPI REST service with security middleware
- OpenClaw live bridge
- Mock and live mode support
- Clear docs and release notes
- Tests for core scaffolding

### Should-have
- Better fallback handling when live skill data is partial
- Better validation against live skill schemas
- Improved examples and screenshots

### Nice-to-have
- Watchlists
- Saved research reports
- Optional web UI
- Deeper live market context injected into the premium daily Square post engine

---

## 15. Success Metrics

### Product quality
- User can get a useful token brief in one turn
- User can generate a Square-ready post from a brief
- Outputs remain risk-aware and structured

### Technical quality
- Compile checks pass
- Test suite passes
- Live adapter path works with real runtime outputs
- Square post succeeds with valid credentials
- API security middleware functions correctly

### Product fit
- Users understand not only what is moving, but whether it is worth attention

---

## 16. Current State

The project currently has:
- A real 10-command research surface
- Live Binance Square posting and scheduled daily engine
- FastAPI REST API (v0.2.1) with security middleware
- OpenClaw live bridge (v0.2.0) for core commands
- Mock and live mode switching via service factory
- Security hardening: HMAC auth, rate limiting, SSRF/path traversal protection, security headers, non-root container
- Binance Spot read-only grounding for price, brief, watchtoday, and supporting token/signal confirmation
- Comprehensive test suite and CI/CD pipeline

Still remaining for full live readiness:
- Real Binance Skills runtime invocation in production flow
- Real payload validation against live outputs
- Wallet and meme live bridge context improvement
- Final deployment hardening
- Final end-to-end verification

---

## 17. Roadmap Summary

### Phase 1 — Research MVP (complete)
- Strong research command scaffold
- Token / wallet / signal / watchtoday / price / brief / risk / audit / meme briefs
- Square-ready output and scheduled publishing engine
- FastAPI REST service and security hardening

### Phase 2 — Live Binance Skills Alignment (in progress)
- Wire real Binance Skills runtime flows
- Validate schemas and field mappings
- Improve fallback and real-data heuristics
- Strengthen wallet and meme live context

### Phase 3 — Product Polish
- Add beginner/pro mode
- Add shareable summary mode
- Improve risk tags and conviction labels
- Add better examples and screenshots
- Improve fallback messaging from partial live skill failures

### Phase 4 — Long-Term Productization
- Add watchlists and saved preferences
- Add persistent reports/history
- Add optional web UI
- Add optional alerts and scheduled digests
- Consider `spot` only as a later, explicitly gated, higher-risk execution capability

---

## 18. Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.10+ (3.12 in Docker) |
| API framework | FastAPI | 0.135.1 |
| ASGI server | uvicorn | 0.41.0 |
| HTTP client | httpx | 0.28.1 |
| Terminal formatting | rich | 13.7.1 |
| Configuration | python-dotenv | 1.2.2 |
| Container | Docker | Python 3.12-slim |
| Testing | Custom runner | tests/run_tests.py (33 test files) |
| CI/CD | GitHub Actions | python-checks.yml |

---

## 19. Final Positioning

Bibipilot is not just another crypto assistant.

It is a **signal-and-risk research copilot** that turns Binance Skills outputs into clearer conviction — and then turns good insight into a Binance Square-ready post.

It prioritizes safety, honesty, and research quality over hype, volume, or execution speed.
