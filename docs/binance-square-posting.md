# Binance Square Posting

## Environment
- `BINANCE_SQUARE_API_KEY`
- `BINANCE_SQUARE_API_BASE_URL`
- `BINANCE_SQUARE_API_PUBLISH_PATH`
- `BINANCE_SQUARE_API_KEY_HEADER`

## Drafting
```bash
python3 src/square_cli.py token BNB
python3 src/square_cli.py signal DOGE
python3 src/square_cli.py watchtoday
python3 src/square_diary.py night-diary --dry-run
```

## Publishing
```bash
python3 src/square_cli.py token BNB --publish
python3 src/square_diary.py night-diary --publish
```

## Behavior
- Draft mode is the default and should be used first.
- The publisher masks API keys in CLI output.
- Successful publish responses are converted into `https://www.binance.com/square/post/{id}` URLs when Binance returns a content id.
- Scheduled posting is handled by `scripts/install_square_diary_cron.sh`.

## Safety notes
- Do not hardcode Square credentials.
- Keep `.env` private.
- Treat publish mode as an operational action, not a test helper.
