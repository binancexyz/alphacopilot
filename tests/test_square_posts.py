from src.models.schemas import AnalysisBrief
from src.services.square_posts import build_square_post, publish_square_post


def test_build_square_post_contains_key_fields():
    brief = AnalysisBrief(
        entity="Token: BNB",
        quick_verdict="BNB looks worth monitoring.",
        signal_quality="High",
        top_risks=["Need volume confirmation."],
        what_to_watch_next=["signal confirmation"],
        conviction="Medium",
    )
    out = build_square_post(brief, max_chars=280)
    assert "BNB looks worth monitoring." in out
    assert "Signal Quality: High" in out


def test_publish_square_post_dry_run():
    result = publish_square_post("hello world", dry_run=True)
    assert result.ok is True
    assert result.mode == "dry-run"
