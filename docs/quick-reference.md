# Quick Reference

## Canonical CLI
```bash
python3 src/main.py brief BNB
python3 src/main.py brief BNB deep
python3 src/main.py signal DOGE
python3 src/main.py audit BNB
python3 src/main.py portfolio
python3 src/main.py wallet 0x1234567890ab
python3 src/main.py watchtoday
python3 src/main.py alpha
python3 src/main.py alpha BNB
python3 src/main.py futures BTC
```

## REST API
All API routes are `GET` routes.

| Path | Purpose |
|------|---------|
| `/health` | system status, guard status, and config warnings |
| `/runtime/report` | rendered runtime health metadata |
| `/brief?symbol=BNB` | compact token brief |
| `/brief?symbol=BNB&deep=true` | deeper token brief |
| `/signal?token=DOGE` | signal validation |
| `/audit?symbol=BNB` | audit-focused brief |
| `/portfolio` | portfolio posture |
| `/wallet?address=0x...` | external wallet posture |
| `/watchtoday` | market board |
| `/alpha?symbol=BNB` | Binance Alpha board or symbol-specific Alpha view |
| `/futures?symbol=BTC` | Binance Futures positioning view |

Compatibility alias: `/holdings` and `/holdings?address=0x...` still work, but `portfolio` and `wallet` are canonical.

## Bridge API
```bash
curl -H 'X-API-Key: replace-me' \
  'http://127.0.0.1:8010/runtime?command=token&entity=BNB'
```

Supported bridge commands: `token`, `signal`, `wallet`, `watchtoday`, `audit`, `meme`, `portfolio`, `alpha`, `futures`.

## Square publishing
```bash
python3 src/square_cli.py token BNB
python3 src/square_cli.py token BNB --publish
python3 src/square_diary.py night-diary --dry-run
```

## Checks
```bash
make check
make test
```
