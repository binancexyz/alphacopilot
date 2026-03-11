# Checks Reference

## Local compile check
```bash
make check
```

## Local test run
```bash
make test
```

## Demo command run
```bash
scripts/demo_capture.sh
```

## Combined helper
```bash
scripts/check_all.sh
```

## API runtime sanity checks
```bash
curl -H 'X-API-Key: ...' http://localhost:8000/health
curl -H 'X-API-Key: ...' http://localhost:8000/runtime/report
```

If auth is disabled, you can omit the header.

## Why this matters
These commands make it easy to verify the scaffold still works before pushing changes.
