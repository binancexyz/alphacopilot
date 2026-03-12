# MVP Definition

## Product promise
Bibipilot helps users understand not just what is moving, but whether it is actually worth attention.

## Current command surface (10 commands)
| Command | Purpose |
|---------|---------|
| `/price <symbol>` | Compact market card with Binance Spot data |
| `/brief <symbol>` | Fast market synthesis with exchange grounding |
| `/token <symbol>` | Token setup and conviction read |
| `/signal <token>` | Smart-money signal timing validation |
| `/wallet <address>` | Wallet behavior and follow verdict |
| `/risk <symbol>` | Downside-first risk assessment |
| `/audit <symbol>` | Security-first token audit |
| `/watchtoday` | Daily market board with live lanes |
| `/meme <symbol>` | First-pass meme token scan |
| `careers` | Binance ecosystem intelligence |

## Output shape
- Quick Verdict
- Signal Quality
- Top Risks
- Why It Matters
- What To Watch Next
- Risk Tags (when applicable)
- Conviction

## Key differentiators
- Signal and risk together in one view
- Wallet behavior interpretation (not just a holdings list)
- Risk tags with severity labels
- Conviction levels (Growing / Stable / Declining)
- Concise, structured output format
- Publishable to Binance Square
- Scheduled premium daily posting engine
- Security-hardened REST API

## Surfaces beyond CLI
- **FastAPI REST API** (v0.2.1) — 8 endpoints with security middleware
- **OpenClaw bridge** (v0.2.0) — live runtime integration
- **Binance Square** — draft/publish with scheduled daily engine

## Non-goals
- Full auto-trading
- Giant frontend dashboard
- Portfolio syncing
- Excessive feature surface
