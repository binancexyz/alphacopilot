# Live Runtime Handoff

If you are the next person implementing live runtime behavior, start here.

## Goal
Replace mock service outputs with real runtime payloads while keeping the analysis/formatting layers unchanged.

## Files that matter most
- `src/services/live_extractors.py`
- `src/services/normalizers.py`
- `src/analyzers/token_live_brief.py`
- `src/analyzers/signal_live_brief.py`
- `src/analyzers/wallet_live_brief.py`
- `src/analyzers/watchtoday_live_brief.py`
- `src/services/runtime_bridge_templates.py`

## Recommended first implementation
Implement `/token` end-to-end first.

## Rule
Do not mix raw tool collection with interpretation logic.
Keep these layers separate:
- runtime/raw collection
- extraction/normalization
- analysis
- formatting
