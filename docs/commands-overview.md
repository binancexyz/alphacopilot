# Commands Overview

## `/price <symbol>`
**Purpose:** Show a compact market card.
- Prefer Binance Spot read-only market data when available
- Surface spread / exchange-pair context instead of just a raw quote

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

**Example:** `python3 src/main.py signal DOGE`

---

## `/wallet <address>`
**Purpose:** Interpret wallet concentration, behavior, and exposure.
- Summarize whether the wallet is worth monitoring
- Provide behavior-aware analysis (not just a holdings snapshot)
- Follow verdict based on trading patterns

**Example:** `python3 src/main.py wallet 0x1234567890ab`

---

## `/portfolio`
**Purpose:** Read your Binance Spot account in a safe, read-only way.
- Uses signed Binance API account-read endpoints
- Estimates visible USD value from current spot prices
- Summarizes top holdings, concentration, stablecoin share, and current posture
- Does not place trades or manage orders

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
- Only valid when `hasResult=true` and `isSupported=true`

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

## Output Shape (all commands)
- Quick Verdict
- Signal Quality / Conviction
- Top Risks
- Why It Matters
- What To Watch Next
- Risk Tags (when applicable)
