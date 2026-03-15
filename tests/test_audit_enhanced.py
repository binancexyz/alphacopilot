from src.analyzers.audit_analysis import _rugpull_score


def test_rugpull_score_blocked_high():
    score, note = _rugpull_score(
        audit_gate="BLOCK",
        audit_flags=["scam detected"],
        concentration=85.0,
        liquidity=50_000,
        buy_tax=0,
        sell_tax=15,
    )
    assert score >= 70
    assert "High" in note
    print("PASS test_rugpull_score_blocked_high")


def test_rugpull_score_clean_low():
    score, note = _rugpull_score(
        audit_gate="ALLOW",
        audit_flags=[],
        concentration=20.0,
        liquidity=10_000_000,
        buy_tax=0,
        sell_tax=0,
    )
    assert score < 40
    assert "Low" in note
    print("PASS test_rugpull_score_clean_low")


def test_rugpull_score_moderate_with_high_tax():
    score, note = _rugpull_score(
        audit_gate="WARN",
        audit_flags=["not verified"],
        concentration=55.0,
        liquidity=80_000,
        buy_tax=0,
        sell_tax=12,
    )
    # WARN=10, not verified=15, sell_tax>=10=20, concentration>=50=8, thin liquidity=10 → 63
    assert 40 <= score < 70, f"Expected 40-70 but got {score}"
    assert "Moderate" in note
    print("PASS test_rugpull_score_moderate_with_high_tax")


def test_rugpull_score_honeypot():
    score, note = _rugpull_score(
        audit_gate="BLOCK",
        audit_flags=["honeypot detected"],
        concentration=90.0,
        liquidity=10_000,
        buy_tax=5,
        sell_tax=50,
    )
    assert score >= 70
    assert "honeypot" in note.lower()
    print("PASS test_rugpull_score_honeypot")


def test_rugpull_score_caps_at_100():
    score, note = _rugpull_score(
        audit_gate="BLOCK",
        audit_flags=["scam", "honeypot", "hidden owner"],
        concentration=95.0,
        liquidity=100,
        buy_tax=20,
        sell_tax=50,
    )
    assert score <= 100
    print("PASS test_rugpull_score_caps_at_100")
