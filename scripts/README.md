# Scripts

## `check_all.sh`
Runs local compile and test checks.

## `demo_capture.sh`
Runs the four core commands in sequence to produce demo-friendly terminal output.

## `summary.sh`
Prints a quick project summary.

## `export_examples.sh`
Exports current command outputs into generated example files.

## `release_prep.sh`
Runs a simple pre-release sanity path and captures demo output.

## `runtime_demo_all.sh`
Runs the runtime-payload demo flow for all four core commands.

## `setup_local_env.sh`
Creates `.venv`, installs requirements, and prepares a local `.env` from template.

## `run_and_test.sh`
Activates `.venv`, runs checks/tests, and performs a quick smoke test.

## `fill_env_checklist.sh`
Shows which live env values should be filled before real usage.

## `install_square_diary_cron.sh`
Installs the current premium 1-post/day Binance Square schedule in `Asia/Phnom_Penh`:
- 21:30 — `night-diary`

The scheduler now works with a stronger quality layer around `src/square_diary.py`, including:
- quality guardrails / cringe filter
- performance logging to `tmp/square_post_log.jsonl`
- topic rotation memory
- premium daily quality guardrails for one high-standard post
- slot-specific hooks, voice, and series labels
- CTA rotation for interaction
- weekly recap generation in `tmp/square_weekly_recap.md`
- a stronger BNB ecosystem intelligence pack for ecosystem-aware post generation

Operationally, treat the current product as **Square post publishing only**. Article publishing is not currently supported.
