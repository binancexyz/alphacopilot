# Live Runtime Pseudocode

## `/token`
```python
symbol = parse_symbol(user_input)
raw_payload = {
    "query-token-info": call_tool("query-token-info", symbol),
    "crypto-market-rank": call_tool("crypto-market-rank", symbol),
    "trading-signal": call_tool("trading-signal", symbol),
    "query-token-audit": call_tool("query-token-audit", symbol),
}
ctx_dict = extract_token_context(raw_payload, symbol)
ctx = normalize_token_context(ctx_dict)
brief = build_token_brief(ctx)
return format_brief(brief)
```

## `/signal`
```python
token = parse_symbol(user_input)
raw_payload = {
    "trading-signal": call_tool("trading-signal", token),
    "query-token-info": call_tool("query-token-info", token),
    "query-token-audit": call_tool("query-token-audit", token),
}
ctx_dict = extract_signal_context(raw_payload, token)
ctx = normalize_signal_context(ctx_dict)
brief = build_signal_brief(ctx)
return format_brief(brief)
```
