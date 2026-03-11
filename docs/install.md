# Install / Run

## Requirements
- Python 3.10+ (3.12 recommended, used in Docker)
- For local venv setup on Ubuntu/Debian: `python3-venv`

## Quick start
```bash
git clone https://github.com/binancexyz/bibipilot.git
cd bibipilot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## CLI usage
```bash
python3 src/main.py price BNB
python3 src/main.py brief BTC
python3 src/main.py token BNB
python3 src/main.py signal DOGE
python3 src/main.py wallet 0x1234567890ab
python3 src/main.py risk ETH
python3 src/main.py audit BNB
python3 src/main.py watchtoday
python3 src/main.py meme DOGE
python3 src/main.py careers
```

## API quick start
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make api
```

The API runs at `http://localhost:8000`. Check `/health` for status.

## Docker quick start
```bash
docker build -t bibipilot .
docker run --rm -p 8000:8000 -e APP_MODE=mock bibipilot
```

## Environment
Copy `.env.example` to `.env` when you start wiring live integrations.

Bibipilot auto-loads `.env` and `.env.local` values when present, so environment variables do not need to be manually exported each time.

## Development checks
```bash
make check   # compile checks
make test    # test suite
```

## Current mode
Default mode is `mock` (`APP_MODE=mock`). That means the scaffold works offline while the live Binance/OpenClaw integration can be tested with `APP_MODE=live`.

## Dependencies
| Package | Version | Purpose |
|---------|---------|---------|
| python-dotenv | 1.2.2 | Environment variable loading |
| rich | 13.7.1 | Terminal output formatting |
| fastapi | 0.135.1 | REST API framework |
| uvicorn | 0.41.0 | ASGI server |
| httpx | 0.28.1 | HTTP client for API calls |
