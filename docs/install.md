# Install / Run

## Requirements
- Python 3.10+
- for local venv setup on Ubuntu/Debian: `python3-venv`

## Quick start
```bash
cd bibipilot
make check
make test
python3 src/main.py token BNB
python3 src/main.py watchtoday
python3 src/main.py wallet 0x1234567890ab
python3 src/main.py signal DOGE
```

## API quick start
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make api
```

## Environment
Copy `.env.example` to `.env` when you start wiring live integrations.

## Current mode
Default mode is `mock`.
That means the scaffold works now, while the live Binance/OpenClaw integration can be added incrementally later.
