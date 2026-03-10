# Runtime Demo

This command-line entrypoint simulates the future live runtime path by loading raw JSON payloads and pushing them through the runtime bridge stub.

## Examples
```bash
python3 src/runtime_demo.py token BNB examples/payloads/token-bnb.json
python3 src/runtime_demo.py signal DOGE examples/payloads/signal-doge.json
python3 src/runtime_demo.py wallet 0x1234567890ab examples/payloads/wallet-sample.json
python3 src/runtime_demo.py watchtoday examples/payloads/watchtoday-sample.json
```

## Why this matters
It makes the live-integration path more tangible before the actual OpenClaw/Binance runtime wiring is finished.
