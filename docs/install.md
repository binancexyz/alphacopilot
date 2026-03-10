# Install / Run

## Requirements
- Python 3.10+

## Quick start
```bash
cd binance-alpha-copilot
make check
make test
python3 src/main.py token BNB
python3 src/main.py watchtoday
python3 src/main.py wallet 0x1234567890ab
python3 src/main.py signal DOGE
```

## Environment
Copy `.env.example` to `.env` when you start wiring live integrations.

## Current mode
Default mode is `mock`.
That means the scaffold works now, while the live Binance/OpenClaw integration can be added incrementally later.
