from src.config import settings
from src.models.schemas import AnalysisBrief
from src.services.square_posts import build_square_post, masked_square_key, publish_square_post


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
    assert "🧩 BNB" in out
    assert "BNB looks worth monitoring." in out
    assert "Need volume confirmation." in out


def test_publish_square_post_dry_run():
    result = publish_square_post("hello world", dry_run=True)
    assert result.ok is True
    assert result.mode == "dry-run"


def test_masked_square_key_masks_full_secret():
    old = settings.square_api_key
    settings.square_api_key = "abcde12345xyz9"
    try:
        assert masked_square_key() == "abcde...xyz9"
    finally:
        settings.square_api_key = old
