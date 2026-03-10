from src.services.live_extractors import extract_signal_context, extract_token_context
from src.services.live_payload_examples import TOKEN_RAW_EXAMPLE


def test_extract_token_context():
    ctx = extract_token_context(TOKEN_RAW_EXAMPLE, "BNB")
    assert ctx["symbol"] == "BNB"
    assert ctx["signal_status"] == "watch"
    assert "Signal may weaken if volume does not confirm." in ctx["major_risks"]


def test_extract_signal_context():
    raw = {
        "trading-signal": {"status": "watch", "summary": "Momentum improving.", "risks": ["Fragile setup"]},
        "query-token-audit": {"flags": ["owner privileges"], "risks": ["Contract risk remains"]},
    }
    ctx = extract_signal_context(raw, "DOGE")
    assert ctx["token"] == "DOGE"
    assert ctx["signal_status"] == "watch"
    assert "Contract risk remains" in ctx["major_risks"]
