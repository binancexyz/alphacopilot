from src.formatters.brief_formatter import format_brief
from src.models.schemas import AnalysisBrief


def test_compact_brief_thin_copy_uses_limited_read_language():
    brief = AnalysisBrief(
        entity="Brief: BNB",
        quick_verdict="BNB|BNB|0|0|0|unknown|0|Runtime detail: HTTP live mode requires the optional dependency 'httpx'. Install requirements.txt or use file:// live mode|Monitor only. No conviction setup.",
        signal_quality="Low",
    )
    rendered = format_brief(brief)
    assert "Signal: Signal not confirmed" in rendered
    assert "Trend: Limited read" in rendered



def test_watchtoday_thin_copy_is_less_placeholder_like():
    brief = AnalysisBrief(
        entity="Market Watch",
        quick_verdict="Quiet board. Hold posture.",
        signal_quality="Low",
        top_risks=["Runtime detail: HTTP live mode requires the optional dependency 'httpx'. Install requirements.txt or use file:// live mode"],
    )
    rendered = format_brief(brief)
    assert "No clean board leader yet" in rendered
    assert "Signal breadth is limited" in rendered
    assert "Attention is limited" in rendered



def test_token_thin_copy_uses_signal_not_confirmed():
    brief = AnalysisBrief(
        entity="Token: BNB",
        quick_verdict="Thin read. No conviction yet.",
        signal_quality="Low",
        top_risks=["Runtime detail: HTTP live mode requires the optional dependency 'httpx'. Install requirements.txt or use file:// live mode"],
        audit_gate="WARN",
    )
    rendered = format_brief(brief)
    assert "Signal: Signal not confirmed" in rendered
