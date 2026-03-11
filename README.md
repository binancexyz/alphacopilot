# Bibipilot

**Bibipilot checks what’s moving, filters what’s dangerous, and publishes what’s worth attention.**

Bibipilot is a **Binance-native research copilot** built around a simple workflow:

**research -> judgment -> publishing**

It uses Binance Skills as the evidence layer, adds a judgment layer on top, and can turn useful output into Binance Square posts.

> Status: **public alpha**
>
> Bibipilot already has a real command surface, live Binance Square publishing proof, and partially live bridge/runtime coverage. It is not finished, but it is well beyond concept stage.

---

## Why Bibipilot exists

Crypto users can already find plenty of raw movement:
- token activity
- wallet activity
- smart-money signals
- trending sectors
- risk tools

The harder part is deciding:
- what is real
- what is risky
- what is late
- what is worth publishing

Bibipilot is designed for that gap.

It does not try to be a full autonomous trading system.
It tries to be the layer between **raw crypto signals** and **usable conviction**.

---

## What it does

Bibipilot currently supports:

- `/price` — compact market card
- `/brief` — fast synthesis
- `/risk` — downside-first risk read
- `/audit` — security-first audit card
- `/token` — token setup and conviction read
- `/signal` — timing and setup validation
- `/wallet` — wallet interpretation with follow verdict
- `/watchtoday` — daily market board with live lanes
- `/meme` — first-pass meme scan
- `careers` — Binance hiring pulse for ecosystem/company-priority context

It also supports Binance Square publishing, a scheduled content engine, and a lightweight Binance Careers pulse for ecosystem intelligence.

---

## What makes it different

### 1. It has a real judgment layer
Bibipilot does not stop at surfacing movement.
It tries to answer:
- should I care?
- should I trust this?
- should I avoid this?
- should this be published?

### 2. It is Binance-native
Bibipilot is built around Binance Skills for evidence, Binance Spot market data for exchange-native price context, and Binance Square for output.

### 3. It has a real publishing loop
Bibipilot is not just an analysis interface.
It can publish live text posts to Binance Square and already includes a scheduled posting engine.

### 4. It is command-specific
Each command is shaped for its own job rather than forcing everything into one generic answer template.

---

## Current architecture

### Evidence layer
Primary research skills:
- `query-token-info`
- `query-token-audit`
- `query-address-info`
- `trading-signal`
- `crypto-market-rank`
- `meme-rush`

### Publishing layer
- `square-post`

### Deferred execution
- `spot`

### Product logic
Binance Skills provide evidence.
Bibipilot adds judgment.
Binance Square becomes the publishing layer.

---

## Quick start

### 1. Clone and install
```bash
git clone https://github.com/binancexyz/bibipilot.git
cd bibipilot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Basic CLI usage
```bash
python3 src/main.py price BNB
python3 src/main.py brief BTC
python3 src/main.py audit BNB
python3 src/main.py signal BNB
python3 src/main.py wallet 0x1234567890ab
python3 src/main.py watchtoday
python3 src/main.py meme DOGE
python3 src/main.py careers
python3 src/main.py careers --cache-only
```

### 3. Optional API mode
```bash
make api
```

---

## What works especially well today

- trust / evidence honesty is stronger across the core commands
- Binance Spot read-only grounding now strengthens `price`, `brief`, and `watchtoday`
- `token` and `signal` can use Binance Spot as supporting exchange-native confirmation
- `wallet` is more behavior-aware and less likely to overread one snapshot
- live mode now exposes runtime health diagnostics through `/health`

## What is still partial

- live bridge coverage is strongest for `token`, `signal`, `audit`, and `watchtoday`
- `wallet` and `meme` still depend on thinner live runtime context than the rest
- Binance Careers is intentionally an adjacent ecosystem-intelligence lane, not core trading logic
- this is a public alpha research copilot, not a finished autonomous trading system

## Mock mode vs live mode

Bibipilot supports both mock and partially live development paths.

### Mock mode
Useful for:
- local development
- testing formatters
- stable demos without live dependencies

### Live mode
Useful for:
- bridge/runtime testing
- live payload extraction
- Binance Square publishing flows
- Binance Spot read-only market grounding for `price`, `brief`, `watchtoday`, and supporting confirmation in `token` / `signal`

Current live bridge coverage is strongest for:
- `token`
- `signal`
- `audit`
- `watchtoday`

Wallet and meme quality still depend on thinner live context and are still evolving.

The careers pulse is deliberately separate from token/signal logic. Treat it as ecosystem intelligence and company-priority context, not as a direct trading signal.

---

## Binance Square publishing

Bibipilot already includes:
- live Binance Square posting
- draft/publish support
- scheduled premium 1-post/day engine
- Asia/Phnom_Penh cron schedule

This matters because Bibipilot is not only built for internal analysis.
It is also built to produce publishable output.

---

## Safety posture

Bibipilot should currently be understood as:
- read-oriented
- research-first
- human-supervised
- risk-aware

It should **not** be described as a finished autonomous trading system.

If you work on this repo:
- never commit secrets
- keep `.env` private
- keep risk visible in outputs
- prefer lower-confidence wording when live context is incomplete

Also review:
- `SECURITY.md`
- `SECURITY-CHECKLIST.md`

---

## Best docs to start with

- `docs/INDEX.md`
- `docs/judge-cheat-sheet.md`
- `docs/live-proof-appendix.md`
- `docs/submission.md`
- `docs/demo-script.md`
- `docs/demo-operator-sheet.md`
- `docs/binance-spot-integration.md`
- `docs/skill-command-matrix.md`
- `docs/output-evolution-plan.md`
- `docs/install.md`
- `docs/quick-reference.md`
- `examples/current-output-examples.md`

---

## Current proof points

Bibipilot already demonstrates:
- real command surface
- live Binance Square posting
- scheduled posting engine
- partially live bridge/runtime behavior
- audit-aware product logic
- Binance Spot read-only grounding across price / brief / watchtoday and supporting token / signal confirmation
- command-specific UX

That is enough to present it as a product with substance, not just a concept.

---

## Contributing

Contributions that improve these areas are especially useful:
- live integration wiring
- normalized payload extraction
- output quality
- heuristic quality
- docs clarity
- maintainability

See `CONTRIBUTING.md` for details.

---

## License

MIT
