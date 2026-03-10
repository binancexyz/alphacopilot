# Live Data Notes

## Reality Check
To become a real product, Binance Alpha Copilot needs live data wiring.

The current scaffold intentionally separates:
- product behavior
- output design
- service interfaces
- runtime choices

from the live data transport.

## What Still Needs Real Integration
- query-token-info
- query-address-info
- crypto-market-rank
- trading-signal
- query-token-audit
- meme-rush

## Recommended Path

### Option 1 — OpenClaw-first integration
Let OpenClaw call Binance Skills Hub tools, then pass normalized context into the Python formatter / analyzer layer.

### Option 2 — Service adapter layer
Build a Python adapter that fetches data from a future API or wrapper service, then feed normalized context into the analyzers.

## Recommendation
For the challenge, **Option 1 is better** because it keeps OpenClaw central in the project story.
