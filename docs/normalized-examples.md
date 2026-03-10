# Normalized Examples

## Example TokenContext
```python
{
  "symbol": "BNB",
  "display_name": "BNB",
  "price": 612.5,
  "liquidity": 125000000.0,
  "holders": 1850000,
  "market_rank_context": "large-cap with strong liquidity and ecosystem relevance",
  "signal_status": "watch",
  "signal_trigger_context": "momentum improving but not fully confirmed",
  "audit_flags": [],
  "major_risks": [
    "Momentum may weaken if broader market cools.",
    "Signal still needs confirmation."
  ]
}
```

## Example WalletContext
```python
{
  "address": "0x123...",
  "portfolio_value": 245000.0,
  "holdings_count": 12,
  "top_holdings": [
    {"symbol": "BNB", "weight_pct": 41.2},
    {"symbol": "DOGE", "weight_pct": 19.8}
  ],
  "top_concentration_pct": 61.0,
  "change_24h": 8.4,
  "notable_exposures": ["meme", "AI"],
  "major_risks": [
    "Low diversification.",
    "Narrative dependence is elevated."
  ]
}
```
