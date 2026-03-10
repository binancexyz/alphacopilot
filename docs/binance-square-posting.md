# Binance Square Posting

This repo now includes a safe scaffold for Binance Square short-post drafting and publishing.

## Safety model
- the API key is read from environment variables only
- do not hardcode it in source files
- do not commit `.env`
- use draft mode first before enabling publish mode

## Environment variables
- `BINANCE_SQUARE_API_KEY`
- `BINANCE_SQUARE_API_BASE_URL`
- `BINANCE_SQUARE_API_PUBLISH_PATH` (default: `/posts`)
- `BINANCE_SQUARE_API_KEY_HEADER` (default: `X-API-Key`)

## Draft a post
```bash
python3 src/square_cli.py token BNB
python3 src/square_cli.py signal DOGE
python3 src/square_cli.py watchtoday
```

## Publish a post
```bash
python3 src/square_cli.py token BNB --publish
```

## Important
Publishing will only work after the real Binance Square endpoint and header/body spec are confirmed.

Current default request shape is:
- method: `POST`
- header: configurable API key header
- body: `{ "text": "..." }`

If Binance Square expects a different path or payload shape, update `src/services/square_posts.py` accordingly.
