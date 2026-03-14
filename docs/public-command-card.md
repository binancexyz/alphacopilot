# Public Command Card

A one-page public command reference for Bibipilot.

## Command Surface

| Command | What it does | Best use |
|---------|---------------|----------|
| `/brief <symbol>` | Fast default asset read | Quick first-pass judgment |
| `/brief <symbol> deep` | Richer asset read under the same brief family | Deeper asset judgment |
| `/signal <symbol>` | Setup quality, invalidation, and risk | Timing / setup checks |
| `/audit <symbol>` | Safety-first asset check | Structural trust / caution |
| `/holdings` | Private Binance Spot posture | Your account posture |
| `/holdings <address>` | External wallet behavior read | Public wallet study |
| `/watchtoday` | Daily market board | What matters today |
| `/alpha` | Binance Alpha overview board | Discovery / board read |
| `/alpha <symbol>` | Binance Alpha token detail | Alpha-token drill-down |
| `/futures <symbol>` | Binance Futures positioning read | Perp / leverage posture |

## Product Map

- **Research** → `/brief`, `/brief deep`, `/watchtoday`, `/alpha`
- **Judgment** → `/signal`, `/audit`
- **Posture** → `/holdings`, `/futures`

## Output Shape

Most commands follow the same compact pattern:

```text
[Header]

[Main state block]

[Verdict + dots]

[⚠️ footer]
```

### Main state blocks by command
- `/brief` → `⚡ Snapshot`
- `/signal` → `⚡ Setup`
- `/audit` → `⚡ Findings`
- `/holdings` → `⚡ Posture`
- `/holdings <address>` → `⚡ Behavior`
- `/watchtoday` → `⚡ Signals` + `🔥 Attention`
- `/alpha` → Alpha board / Alpha market snapshot
- `/futures` → Futures positioning snapshot

## Real Current Example Shapes

### `/brief BNB`
```text
**🧩 BNB $659.84 +2.53% 📈 #4**

**⚡ Snapshot**
┣ Signal: No clear entry
┣ Trend: Defensive drift
┗ Liquidity: $59.0M

**🧠 Verdict 🟡⚪⚪⚪**
More of a monitor than a conviction setup right now.

**⚠️ Secondary data · Market-only read**
```

### `/watchtoday`
```text
**🌐 Watchtoday**

**⚡ Signals**
┣ 万事币安 — 7 smart-money wallets | BUY
┣ SAFE — 4 smart-money wallets | BUY
┗ Fight — 5 smart-money wallets | BUY

**🔥 Attention**
┣ quq — 41 searches | Liq $2.7M
┣ RAVE — 30 searches | Liq $1.2M
┗ WMTX — 21 searches | Liq $1.4M

**🧠 Board 🟢🟢🟢⚪**
Opportunity visible. Be selective.

**⚠️ Attention ≠ signal · RAVE: concentration + audit ⚠️**
```

### `/holdings`
```text
**📂 Holdings Binance Spot ~$1,640.15**

**⚡ Posture**
┣ Stables: 62.9% 💵
┣ Risk: 37.1%
┗ Top asset: USDC

**💼 Top Holdings**
┣ USDC ~$618.12 (37.7%) | includes LD balances
┣ USDT ~$414.18 (25.3%) | includes LD balances
┗ ASTER ~$265.62 (16.2%) | includes LD balances

**🧠 Verdict 🟢🟢🟢⚪**
Defensive. Dry powder ready. No overconcentration.

**⚠️ Snapshot saved 1m ago · Read-only estimate**
```

## Publishing Flow

Default publishing flow from now on:
1. run `/watchtoday`
2. build draft from the current board
3. show draft for confirmation
4. publish only after explicit approval

## Honest Readiness

### Strongest now
- `/watchtoday`
- `/holdings`
- `/brief`

### Still improving with thinner live depth
- `/brief deep`
- `/signal`
- `/audit`
- `/holdings <address>`
