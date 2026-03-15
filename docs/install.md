# Install

## Requirements
- Python 3.10 or newer
- `python3-venv` if you are creating a local virtualenv

## Local setup
```bash
git clone https://github.com/binancexyz/bibipilot.git
cd bibipilot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## First commands
```bash
python3 src/main.py brief BTC
python3 src/main.py brief BNB deep
python3 src/main.py signal DOGE
python3 src/main.py audit BNB
python3 src/main.py holdings
python3 src/main.py holdings 0x1234567890ab
python3 src/main.py watchtoday
```

## Local API
```bash
make api
```

Default listen address is `http://127.0.0.1:8000`.

## Local checks
```bash
make check
make test
```

## Runtime modes
- `APP_MODE=mock` is the default developer mode.
- `APP_MODE=live` requires `BINANCE_SKILLS_BASE_URL`.
- Account-backed portfolio flows also require `BINANCE_API_KEY` and `BINANCE_API_SECRET`.

## Environment notes
- `.env` and `.env.local` are auto-loaded by `src/config.py`.
- Use `BRIDGE_API_KEY` when your live runtime adapter requires request authentication.
- Use `API_AUTH_ENABLED=true` and `API_AUTH_KEY` before exposing the REST API publicly.
- Square publishing requires `BINANCE_SQUARE_API_KEY`.
