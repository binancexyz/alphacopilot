from src.formatters.brief_formatter import format_brief
from src.models.schemas import AnalysisBrief


def test_signal_footer_prefers_dependency_label_over_degraded_duplication():
    brief = AnalysisBrief(
        entity="Signal: DOGE",
        quick_verdict="Watchlist only. Needs confirmation.",
        signal_quality="Low",
        top_risks=[
            "Live bridge is unavailable for signal; using degraded context.",
            "Runtime detail: HTTP live mode requires the optional dependency 'httpx'. Install requirements.txt or use file:// live mode",
        ],
        audit_gate="WARN",
    )
    rendered = format_brief(brief)
    assert "Runtime dependency missing" in rendered
    assert "Live bridge limited · Runtime dependency missing" not in rendered



def test_watchtoday_footer_prefers_clean_runtime_labels():
    brief = AnalysisBrief(
        entity="Market Watch",
        quick_verdict="Quiet board. Hold posture.",
        signal_quality="Low",
        top_risks=[
            "Live bridge is unavailable for watchtoday; using degraded context.",
            "Runtime detail: HTTP live mode requires the optional dependency 'httpx'. Install requirements.txt or use file:// live mode",
        ],
    )
    rendered = format_brief(brief)
    assert "Runtime dependency missing" in rendered
    assert "Live bridge limited · Runtime dependency missing" not in rendered
