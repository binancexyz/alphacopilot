# Implementation Sequence

## Step 1 — Already done
- project framing
- docs
- Python scaffold
- command analyzers
- formatter
- mock/live service split

## Step 2 — Live normalization layer
Build the real adapters that map Binance/OpenClaw outputs into:
- TokenContext
- WalletContext
- WatchTodayContext
- SignalContext

## Step 3 — OpenClaw bridge
Wire the runtime so user commands trigger:
- skill calls
- normalization
- Python analysis
- final response formatting

## Step 4 — Improve heuristics
Refine:
- signal quality logic
- conviction logic
- risk tag assignment
- beginner/pro mode

## Step 5 — Demo polish
- screenshots
- demo video
- public README cleanup
- final submission copy
