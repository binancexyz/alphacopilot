# Binance Spot Integration

Bibipilot now uses **Binance Spot read-only market data** as an exchange-native grounding layer.

## Why this matters

This does **not** turn Bibipilot into a trading bot.

It does:
- improve exchange-native price context
- add pair-aware market confirmation
- surface spread-aware caution when available
- make `/watchtoday` feel more like a real Binance market board

It does **not**:
- place trades
- manage user accounts
- use signed trading endpoints
- treat exchange price alone as proof of signal quality

---

## Current usage

### `/price`
Prefers Binance Spot public endpoints first.
Uses:
- `exchangeInfo`
- `ticker/24hr`
- `bookTicker`
- `avgPrice`

### `/brief`
Uses Binance Spot as a grounding layer when available.
This helps Bibipilot distinguish between:
- exchange price context
- actual signal confirmation

### `/watchtoday`
Adds a compact **Exchange Board** lane.
Current board anchors are built from:
- BNB
- BTC
- SOL

This is intentionally small.
The goal is to anchor the daily board, not turn it into a terminal dump.

### `/token` and `/signal`
Use Binance Spot as a **supporting confirmation layer**.
Examples:
- pair is live, but smart-money signal is still unmatched
- spread is wide, so exchange confirmation is less clean
- exchange price context is active, but conviction still depends on follow-through

---

## Product rule

Binance Spot is a **supporting market-data layer**.
It should strengthen judgment, not replace it.

That means:
- exchange price != valid signal
- live pair != high conviction
- 24h move != publish-worthy thesis

Bibipilot stays research -> judgment -> publishing.
Binance Spot just makes the market side more grounded.
