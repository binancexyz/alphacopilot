# OpenClaw Runtime Bridge

## Goal
Use OpenClaw as the user-facing runtime while keeping the research logic reusable in Python.

## Recommended Flow

### 1. User sends a command
Examples:
- `/brief BNB`
- `/brief BNB deep`
- `/holdings 0x...`
- `/watchtoday`
- `/signal DOGE`

### 2. OpenClaw handles interaction
OpenClaw should:
- receive the command
- call relevant Binance Skills Hub tools
- gather raw context
- pass normalized context into the Python analysis layer

### 3. Python builds the final research brief
The Python layer should:
- synthesize signal and risk context
- attach risk tags
- compute a conviction label
- format the response consistently

### 4. OpenClaw sends the result back
The final reply should keep the product voice and structure.

## Why this bridge matters
This keeps:
- OpenClaw central for challenge alignment
- Python central for reusable product logic

## Practical note
For the challenge, it is okay if the Python layer remains mostly internal and OpenClaw remains the visible assistant interface.
