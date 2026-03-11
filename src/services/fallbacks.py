from __future__ import annotations


def missing_context_warning(command: str) -> str:
    messages = {
        "token": "Token context is partially available right now, so this view should be treated as lower-confidence.",
        "signal": "Signal context is incomplete right now, so confirmation should be treated cautiously.",
        "wallet": "Wallet context is incomplete right now, so behavior interpretation may be understated.",
        "watchtoday": "Today's market brief is based on partial context, so prioritization may be less reliable than usual.",
        "audit": "Audit context is incomplete right now, so security conclusions should stay cautious.",
        "meme": "Meme context is incomplete right now, so lifecycle and safety conclusions should stay cautious.",
    }
    return messages.get(command, "Context is incomplete right now, so treat this output as lower-confidence.")
