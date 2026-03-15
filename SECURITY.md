# Security Policy

## Reporting a Vulnerability
If you discover a security issue, please avoid posting sensitive details publicly in an issue.

Instead:
- report privately through the appropriate GitHub/security channel if available
- or contact the maintainer directly

## Scope
Be especially careful around:
- API keys
- wallet credentials
- secrets in `.env` files
- runtime integration code that may touch real trading or account access

## Rule
Never commit secrets to the repository.

## Project-specific guidance
Also review:
- `SECURITY-CHECKLIST.md`
- `docs/security-principles.md`
