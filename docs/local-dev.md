# Local Development

## Recommended flow
```bash
cd bibipilot
make check
make test
make token
make signal
```

## Optional shell environment
If you use `direnv`, you can adapt `.envrc.example` into a local `.envrc` for convenient local variables.

## Current default mode
- `APP_MODE=mock`

This keeps the project runnable while live runtime integration is still pending.
