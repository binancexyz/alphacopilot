# Commands Overview

## Recommended product surface

### Core commands
- `/brief <symbol>` — default market read
- `/token <symbol>` — deeper asset judgment
- `/signal <token>` — setup timing and invalidation
- `/portfolio` — private posture
- `/wallet <address>` — public wallet behavior
- `/watchtoday` — daily market board

### Specialist commands
- `/price <symbol>` — lightweight market utility card
- `/risk <symbol>` — downside-only specialist lens
- `/audit <symbol>` — security-first specialist view
- `/meme <symbol>` — meme-specific scan
- `careers` — ecosystem context lane

### Alias
- `watch today` → alias for `/watchtoday`

---

## `/price <symbol>`
**Purpose:** Show a premium market card.
- Prefer Binance Spot read-only market data when available
- Surface spread / exchange-pair context instead of just a raw quote
- Show cleaner source/context framing when secondary market data is used

**Example:** `python3 src/main.py price BNB`

---

## `/brief <symbol>`
**Purpose:** Premium default market read.
- Compress token + signal + market context quickly
- Ground the answer in Binance Spot when available
- Distinguish live exchange price from actual smart-money confirmation
- Best default command when you want the shortest smart answer

**Example:** `python3 src/main.py brief BTC`

---

## `/token <symbol>`
**Purpose:** Analyze token context with full conviction assessment.
- Evaluate signal quality
- Highlight top risks
- Use Binance Spot as supporting exchange-native confirmation when available
- Includes audit, market rank, and trading signal context
- Starts factoring in current portfolio posture when private Spot account context is available

**Example:** `python3 src/main.py token BNB`

---

## `/signal <token>`
**Purpose:** Evaluate whether a smart-money signal is worth attention.
- Show fragility and confirmation conditions
- Distinguish between live exchange price and matched smart-money signal quality
- Show signal timing, direction, and exit rate
- Surface explicit invalidation when possible
- Factors in current portfolio posture when private Spot account context is available

**Example:** `python3 src/main.py signal DOGE`

---

## `/wallet <address>`
**Purpose:** Read public posture from an external wallet.
- Summarize whether the wallet is worth monitoring
- Provide behavior-aware analysis (not just a holdings snapshot)
- Follow verdict based on trading patterns
- Best paired mentally with `/portfolio`, which reads private Binance Spot posture

**Example:** `python3 src/main.py wallet 0x1234567890ab`

---

## `/portfolio`
**Purpose:** Read your private Binance Spot posture in a safe, read-only way.
- Uses signed Binance API account-read endpoints
- Estimates visible USD value from current spot prices
- Summarizes top holdings, concentration, stablecoin share, current posture, freshness, and historical drift
- Does not place trades or manage orders
- Best paired mentally with `/wallet`, which reads public posture from an external address

**Example:** `python3 src/main.py portfolio`

---

## `/risk <symbol>`
**Purpose:** Downside-first risk assessment.
- Identify top risk factors by severity
- Surface what could go wrong
- Risk tags with clear severity labels
- Factors in current portfolio posture when private Spot account context is available

**Example:** `python3 src/main.py risk ETH`

---

## `/audit <symbol>`
**Purpose:** Security-first token audit card.
- Scam/vulnerability detection
- Contract risk assessment
- Risk gate that blocks on critical findings
- Surfaces audit validity more explicitly when live audit visibility is partial
- Only fully valid when `hasResult=true` and `isSupported=true`

**Example:** `python3 src/main.py audit BNB`

---

## `/watchtoday`
**Purpose:** Filter broad market noise into a daily board.
- Prioritize narratives, signals, and risk zones
- Anchor the board with a compact Binance Spot exchange board when available
- Smart-money context and trending narratives
- Factors in current portfolio posture when private Spot account context is available

**Example:** `python3 src/main.py watchtoday`

---

## `/meme <symbol>`
**Purpose:** First-pass meme token scan.
- Meme lifecycle status (new / finalizing / migrated)
- Holder distribution risk
- Launch status and hype assessment

**Example:** `python3 src/main.py meme DOGE`

---

## `careers`
**Purpose:** Binance ecosystem intelligence through hiring data.
- Active hiring areas and team growth signals
- Ecosystem priority context
- Not a trading signal — treat as company intelligence

**Example:** `python3 src/main.py careers` or `python3 src/main.py careers --cache-only`

---

## Output Shape (current command family)
- Structured section-based layout
- Read / Verdict / Risks / Watch blocks where appropriate
- Context / Source / Validity tags when relevant
- Command-specific additions like `Invalidation` for `/signal`
- Premium tree-style hierarchy for grouped outputs
