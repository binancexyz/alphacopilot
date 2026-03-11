# Binance Careers Pulse

Bibipilot now includes a lightweight `careers` lane.

## Why it exists

This is **not** a trading command.
It is an ecosystem-intelligence helper.

Use it to:
- spot where Binance seems to be investing attention
- notice hiring concentration by team or geography
- support content and ecosystem commentary
- add company-priority context around the broader Binance ecosystem

Do **not** use it as:
- direct token buy/sell logic
- core `/signal` input
- proof of market direction by itself

---

## Command

```bash
python3 src/main.py careers
```

Or run the helper directly:

```bash
python3 src/binance_careers.py --refresh
python3 src/binance_careers.py --cache-only
```

---

## Behavior

The careers helper will:
1. try to fetch the Binance Careers page
2. attempt to extract structured job rows from embedded page data
3. save a local cache to `tmp/binance_careers_cache.json`
4. fall back to cache if live refresh fails

This matters because the careers page may sometimes block bot-style requests.

---

## Product rule

Treat careers output as:

**ecosystem / company-priority context**

not as:

**direct market signal**

That keeps Bibipilot focused and avoids forcing weak causal links into token analysis.
