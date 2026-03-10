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
python3 src/square_diary.py education --dry-run
```

## Publish a post
```bash
python3 src/square_cli.py token BNB --publish
python3 src/square_diary.py ecosystem --publish
```

## Scheduled content engine
This repo includes a scheduled Square content engine in `src/square_diary.py`.

Current schedule in `Asia/Phnom_Penh`:
- 07:30 — `morning-diary`
- 09:30 — `education`
- 11:30 — `market`
- 13:30 — `builder`
- 15:30 — `ecosystem`
- 18:30 — `motivation`
- 21:30 — `night-diary`

Install/update the cron schedule with:

```bash
bash scripts/install_square_diary_cron.sh
```

## Quality layer
The scheduled engine now includes:
- stronger rotating hooks by slot and hook type
- slot-specific voice profiles
- topic rotation memory
- CTA / interaction endings
- recurring series labels
- a cringe/generic filter that can block weak posts before publish
- performance logging in `tmp/square_post_log.jsonl`
- article seed capture in `tmp/square_article_seeds.jsonl`
- weekly recap generation in `tmp/square_weekly_recap.md`

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
- the scheduled content engine rotates across diary, education, market, builder, ecosystem, motivation, and reflection content
- the scheduled engine keeps a lightweight local state file at `tmp/square_diary_state.json` to reduce repeated hooks, CTAs, and topics across recurring posts
