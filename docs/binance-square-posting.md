# Binance Square Posting

This repo now includes Binance Square short-post drafting and publishing aligned to the Binance `square-post` skill spec.

## Confirmed API
- Method: `POST`
- URL: `https://www.binance.com/bapi/composite/v1/public/pgc/openApi/content/add`
- Required header: `X-Square-OpenAPI-Key`
- Required header: `Content-Type: application/json`
- Required header: `clienttype: binanceSkill`
- Body field: `bodyTextOnly`

## Safety model
- the API key is read from environment variables only
- do not hardcode it in source files
- do not commit `.env`
- use draft mode first before enabling publish mode
- never display full API keys; mask them if you show them at all

## Environment variables
- `BINANCE_SQUARE_API_KEY`
- `BINANCE_SQUARE_API_BASE_URL` (default: `https://www.binance.com`)
- `BINANCE_SQUARE_API_PUBLISH_PATH` (default: `/bapi/composite/v1/public/pgc/openApi/content/add`)
- `BINANCE_SQUARE_API_KEY_HEADER` (default: `X-Square-OpenAPI-Key`)

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

## Success behavior
On success, Binance returns a content id. The post URL format is:

```text
https://www.binance.com/square/post/{id}
```

## Error notes
Known important codes include:
- `000000` success
- `220009` daily post limit exceeded
- `220003` API key not found
- `220004` API key expired
- `20013` content length limited
- `220011` content body must not be empty
- `10005` identity verification required

## Current implementation notes
- this repo sends `bodyTextOnly`
- this repo sends `clienttype: binanceSkill`
- this repo parses `data.id` and constructs the final post URL when available
