# Normalized Data Contracts

These contracts describe the ideal shape passed from the runtime/tool layer into the Python analysis layer.

## TokenContext
```python
{
  "symbol": "BNB",
  "display_name": "BNB",
  "price": 0.0,
  "liquidity": 0.0,
  "holders": 0,
  "market_rank_context": "high attention / strong liquidity",
  "signal_status": "neutral|bullish|bearish|unknown",
  "signal_trigger_context": "optional short text",
  "audit_flags": ["mintable", "owner privileges"],
  "major_risks": ["..."],
}
```

## WalletContext
```python
{
  "address": "0x...",
  "portfolio_value": 0.0,
  "holdings_count": 0,
  "top_holdings": [
    {"symbol": "BNB", "weight_pct": 42.5},
    {"symbol": "DOGE", "weight_pct": 18.2}
  ],
  "top_concentration_pct": 60.7,
  "change_24h": 0.0,
  "notable_exposures": ["AI", "meme"],
  "major_risks": ["..."],
}
```

## WatchTodayContext
```python
{
  "top_narratives": ["AI", "meme rotation", "L2"],
  "strongest_signals": ["BNB ecosystem strength", "AI token inflows"],
  "risk_zones": ["overheated meme names"],
  "market_takeaway": "Opportunity exists, but filtering matters.",
  "major_risks": ["..."],
}
```

## SignalContext
```python
{
  "token": "DOGE",
  "signal_status": "triggered|watch|none|unknown",
  "trigger_price": 0.0,
  "current_price": 0.0,
  "max_gain": 0.0,
  "exit_rate": 0.0,
  "audit_flags": ["..."],
  "supporting_context": "optional short text",
  "major_risks": ["..."],
}
```

## Design Rule
The runtime/tool layer should do data collection.
The Python analysis layer should do interpretation.
