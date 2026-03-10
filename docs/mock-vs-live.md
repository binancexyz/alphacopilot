# Mock vs Live

## Mock mode
Current default mode.

Purpose:
- demonstrate product behavior
- test output shape
- support fast iteration
- keep the repo runnable immediately

## Live mode
Future integration mode.

Purpose:
- call real Binance Skills Hub data paths
- use OpenClaw runtime orchestration
- normalize live results into Python context objects

## Why both modes matter
Mock mode keeps the project easy to demo and develop.
Live mode makes it real.

The project is intentionally designed to support both without rewriting the core output logic.
