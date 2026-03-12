# Runtime Implementation Notes

## Important constraint
The current repo can prepare the live path, but the real invocation of OpenClaw/Binance live tools must happen inside the runtime environment where those tools are actually available.

## What is prepared already
- extractor functions
- normalized context contracts
- analyzers
- formatter
- runtime bridge templates

## What the next implementation must do
### For `/token`
- gather raw outputs from the four live skills
- build `raw_payload`
- pass to `extract_token_context(...)`
- normalize and interpret
- return formatted brief

## Warning
Do not skip normalization.
Raw runtime outputs will drift over time; the normalized layer protects the rest of the code from churn.
