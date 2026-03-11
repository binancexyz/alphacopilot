# Security Notes

## Best current posture
- read-only
- no trade execution
- no withdrawal permissions
- no secrets in repo
- visible risk language
- human confirmation for any future high-risk actions

## Why this is good for the project
It improves:
- public trust
- contest credibility
- maintainability
- resilience against careless mistakes

## API posture
Current repo now includes lightweight API guardrails:
- optional header-based API key auth
- lightweight in-memory rate limiting

This is useful as public-alpha scaffolding, but a real public deployment should still sit behind a reverse proxy or private network.

## Strong recommendation
Do not add direct execution features until the research path is stable and the runtime boundaries are well tested.
