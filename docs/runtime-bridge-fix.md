# Runtime Bridge Fix

## What was fixed
The runtime bridge live stub previously normalized raw payloads, but then ignored them and called the higher-level analyzers that used mock service mode.

That meant the so-called runtime demo was not truly exercising the raw-payload path.

## New behavior
The bridge now:
1. extracts raw payload into a normalized context
2. passes the normalized context directly into the corresponding live-brief builder
3. formats the resulting brief

## Why this matters
This makes the runtime demo path much closer to the real intended live integration design.

## Affected paths
- token
- signal
- wallet
- watchtoday
