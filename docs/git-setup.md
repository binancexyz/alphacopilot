# Git Setup

## Why this matters
The repo is ready enough that the next important operational step is committing it cleanly.

## Required commands
```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

## Suggested commit flow
```bash
cd /root/.openclaw/workspace/bibipilot
git init
git add .
git commit -m "Initial Bibipilot scaffold"
```

## Suggested next step after commit
Create a GitHub repo named `bibipilot`, then add remote and push.
