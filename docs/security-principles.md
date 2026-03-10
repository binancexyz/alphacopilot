# Security Principles

## 1. Research first, execution later
AlphaCopilot should begin as a research copilot, not an execution bot.

## 2. Least privilege
If API keys are ever used, start with the minimum permissions possible. Read-only is strongly preferred for early versions.

## 3. Normalize before trusting
Do not let raw runtime/tool outputs directly drive user-facing conclusions. Normalize them first.

## 4. Missing data should reduce confidence
If the system lacks audit, ranking, or signal context, lower conviction and say so.

## 5. Keep risk visible
The product should never hide risk in favor of hype.

## 6. Separate research from action
Any future execution path should be clearly separated from research/analysis logic.
