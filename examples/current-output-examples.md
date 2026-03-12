# Current Output Examples

These are current example outputs from the CLI in the repo workspace.
They are useful for demos, README screenshots, and judge-facing proof that the product surface is real.

Note: output formatting was tightened toward a cleaner premium shape. Prefer these examples as current reference examples, but exact live values will vary.

The public product surface is now built around:
- `/brief`
- `/signal`
- `/holdings`
- `/watchtoday`
- `/audit`

---

## `/brief BNB`

```text
**🧩 BNB $651.27 -0.20% 📉 #4**

**⚡ Snapshot**
┣ Signal: No clear entry
┣ Trend: Defensive drift
┗ Liquidity: $58.9M

**🧠 Verdict 🟡⚪⚪⚪**
More of a monitor than a conviction setup right now.

**⚠️ Secondary data**
```

What this shows:
- fast default asset read
- premium compact formatting
- low-friction scan for symbol + price + rank + verdict

---

## `/brief BNB deep`

```text
**🧩 BNB — +0.00% ➖**

**⚡ Snapshot**
┣ Signal: No clear entry
┣ Trend: Defensive drift
┗ Liquidity: —

**🧠 Verdict 🟡⚪⚪⚪**
BNB Chain Native Token is still a provisional read right now because too much live context is incomplete, early, or unmatched.

**⚠️ No matched live smart-money signal is visible on the current board, so this token read stays capped · Defensive market**
```

What this shows:
- deeper asset judgment through the canonical brief entry point
- same compact visual language as default `/brief`
- risk collapsed into one footer line

---

## `/signal BNB`

```text
**📡 BNB — +0.00% ➖**

**⚡ Setup**
┣ Audit: 🟢 Allow
┣ Strength: Low
┗ Invalidation: Breaks if price attention never turns into a matched smart-money signal.

**🧠 Verdict 🟡⚪⚪⚪**
BNB is still a provisional signal read because the live setup evidence is too early or unmatched to trust aggressively.

**⚠️ No smart-money follow-through · Defensive market**
```

What this shows:
- risk folded directly into signal judgment
- invalidation kept explicit
- much tighter product-style setup card

---

## `/holdings`

```text
**📂 Holdings Binance Spot ~$1,634.50**

**⚡ Posture**
┣ Stables: 63.2% 💵
┣ Risk: 36.8%
┗ Top asset: USDC

**💼 Top Holdings**
┣ USDC ~$618.12 (37.8%) | includes LD balances
┣ USDT ~$414.18 (25.3%) | includes LD balances
┗ ASTER ~$264.50 (16.2%) | includes LD balances

**🧠 Verdict 🟢🟢🟢⚪**
This read-only Spot snapshot looks defensive, with meaningful stablecoin dry powder and no extreme single-asset concentration.

**⚠️ Snapshot saved just now · Read-only estimate**
```

What this shows:
- unified private posture command
- compact portfolio view
- quick concentration + dry-powder read

---

## `/holdings 0x1234567890ab`

```text
**👛 0x1234…90ab ⚠️ Unknown**

**⚡ Behavior**
┣ Activity: starts rotating into new assets or stays static
┣ Top move: top holding concentration stays controlled as new positions appear
┗ Drift: wallet starts clustering around a clearer narrative

**🧠 Verdict 🟡⚪⚪⚪**
This wallet does not currently have enough live evidence to justify a strong follow call.

**⚠️ Thin payload · Not a follow signal**
```

What this shows:
- external wallet mode under the same `/holdings` surface
- follow-quality judgment instead of balance dump
- compact behavior-first read

---

## `/watchtoday`

```text
**🌐 Watchtoday**

**⚡ Signals**
┣ 万事币安 — 7 smart-money wallets | BUY
┣ SAFE — 4 smart-money wallets | BUY
┗ Fight — 5 smart-money wallets | BUY

**🔥 Attention**
┣ quq — 40 searches | Liq $2.3M
┣ WMTX — 22 searches | Liq $1.2M
┗ BSB — 73 searches | Liq $1.4M

**🧠 Board 🟢🟢🟢⚪**
Opportunity visible. Be selective.

**⚠️ Attention ≠ signal · WMTX shows audit cautions in market rank context · BSB has extreme top-10 holder concentration**
```

What this shows:
- signals and attention separated cleanly
- no extra narrative clutter
- one clear board verdict

---

## `/audit BNB`

```text
**🔐 BNB Audit: 🟢 Allow Risk: Low**

**⚡ Findings**
┗ No major security issue surfaced in the current audit payload.

**🧠 Verdict 🟡⚪⚪⚪**
BNB Chain Native Token has only limited audit visibility right now, so security conclusions should stay cautious.

**⚠️ Partial validity · Not investment advice**
```

What this shows:
- safety-first read in compact form
- disclaimer collapsed into the footer
- meme lens omitted when not relevant
