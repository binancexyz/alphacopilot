# Final Release Checklist

This is the practical go/no-go checklist for the current repo state.

## Repo quality
- [x] CLI scaffold works in mock mode without optional live HTTP deps
- [x] Live adapter supports file-based payload loading
- [x] Live adapter supports HTTP adapter loading when dependencies are installed
- [x] Runtime bridge can consume raw payloads directly
- [x] API surface exists for serving formatted briefs
- [x] Docker and local startup docs exist

## Must verify on target host
- [ ] `python3-venv` is installed
- [ ] create `.venv`
- [ ] `pip install -r requirements.txt`
- [ ] `make test`
- [ ] `make api`
- [ ] `GET /health` returns OK
- [ ] at least one `/brief/token` live-mode request succeeds

## Security / release hygiene
- [x] `.env` is ignored
- [ ] verify no secrets are committed
- [ ] add auth/rate limiting before any public API exposure
- [ ] confirm API keys are read-only and least-privilege
- [ ] verify no trading/execution actions are enabled

## Demo / launch
- [ ] capture clean screenshots or short demo clip
- [ ] verify output wording on token, signal, wallet, watchtoday
- [ ] rehearse live-mode fallback explanation
- [ ] finalize submission/release copy

## Hard truth
The repo is now strong, but true production readiness still depends on the deployment host and real upstream Binance/OpenClaw runtime access.
