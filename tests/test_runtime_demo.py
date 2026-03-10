import subprocess


def run(*args: str) -> str:
    result = subprocess.run(args, capture_output=True, text=True, check=True)
    return result.stdout


def test_runtime_demo_token():
    out = run("python3", "src/runtime_demo.py", "token", "BNB", "examples/payloads/token-bnb.json")
    assert "Token: BNB" in out


def test_runtime_demo_signal():
    out = run("python3", "src/runtime_demo.py", "signal", "DOGE", "examples/payloads/signal-doge.json")
    assert "Signal: DOGE" in out
