# Architecture Diagram

```text
┌──────────────────────┐
│      Telegram        │
│   / chat interface   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│      OpenClaw        │
│ runtime + routing    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Binance Skills Hub   │
│ live tool outputs    │
└──────────┬───────────┘
           │ raw payloads
           ▼
┌──────────────────────┐
│  Python service /    │
│ normalizer layer     │
└──────────┬───────────┘
           │ normalized contexts
           ▼
┌──────────────────────┐
│ analyzers +          │
│ heuristics           │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ formatters           │
│ final research brief │
└──────────────────────┘
```

## Core idea
OpenClaw orchestrates. Binance Skills Hub provides live capability. Python interprets and formats.
