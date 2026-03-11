# Public Release Message

Launching **Bibipilot**.

It’s a **public-alpha Binance-native research copilot** built around:
- research
- judgment
- publishing

Current command surface includes:
- `/price`
- `/brief`
- `/risk`
- `/audit`
- `/token`
- `/signal`
- `/wallet`
- `/watchtoday`
- `/meme`
- `careers`

Core idea:
**Less noise. Better conviction.**

What is real today:
- runnable Python CLI + API surface
- stronger evidence honesty across the main commands
- Binance Spot read-only grounding for `price`, `brief`, and `watchtoday`
- supporting Binance Spot confirmation for `token` and `signal`
- improved wallet behavior judgment
- Binance Square publishing + premium scheduled daily posting engine
- live runtime health diagnostics via `/health`

What is still partial:
- live bridge coverage is strongest for `token`, `signal`, `audit`, and `watchtoday`
- wallet and meme live depth still need richer runtime context
- this should be treated as a credible public alpha, not a finished autonomous trading system
