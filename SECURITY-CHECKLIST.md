# Security Checklist

Use this checklist before treating Bibipilot as anything more than a research scaffold.

## Secrets
- [ ] No API keys committed to the repo
- [ ] `.env` is ignored by git
- [ ] `.env.example` contains placeholders only
- [ ] No secrets printed in logs or screenshots

## Runtime Safety
- [ ] Runtime uses read-only access for early versions
- [ ] No withdrawal permissions anywhere
- [ ] No live execution or trading actions enabled in MVP
- [ ] High-risk actions require explicit human confirmation

## Architecture Safety
- [ ] Raw tool output is normalized before analysis
- [ ] Runtime logic stays separate from interpretation logic
- [ ] Research path is separated from any future execution path
- [ ] Missing data lowers confidence instead of increasing guesswork

## Output Safety
- [ ] Responses do not promise profits
- [ ] Responses do not present speculation as certainty
- [ ] Risk remains visible in the output
- [ ] Fallback language is used when context is incomplete

## Repo Hygiene
- [ ] Secrets are not present in commits
- [ ] Public repo reviewed before release
- [ ] Security-sensitive issues are not posted publicly in full detail
- [ ] Dependency footprint stays minimal and intentional

## Recommended MVP posture
For best safety, Bibipilot should remain:
- read-only
- research-focused
- signal-and-risk oriented
- human-supervised
