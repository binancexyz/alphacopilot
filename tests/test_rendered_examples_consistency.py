from src.formatters.brief_formatter import format_brief
from src.models.schemas import AnalysisBrief


def test_compact_brief_thin_footer_does_not_duplicate_liquidity_warning():
    brief = AnalysisBrief(
        entity="Brief: BNB",
        quick_verdict="BNB|BNB|0|0|0|unknown|0|Live market quote temporarily unavailable, so this brief is using thinner fallback context.|Monitor only. No conviction setup.",
        signal_quality="Low",
    )
    rendered = format_brief(brief)
    assert "Liquidity: — limited" in rendered
    assert rendered.count("Thin liquidity") == 0
    assert "⚠️ Thin payload" in rendered



def test_token_ownership_block_keeps_three_rows_when_partial():
    brief = AnalysisBrief(
        entity="Token: BNB",
        quick_verdict="Thin read. No conviction yet.",
        signal_quality="Low",
        beginner_note="Smart money: none visible",
        top_risks=["Runtime detail: HTTP live mode requires the optional dependency 'httpx'. Install requirements.txt or use file:// live mode"],
    )
    rendered = format_brief(brief)
    assert "💼 Ownership" in rendered
    assert "Holders: —" in rendered
    assert "Smart money: none visible" in rendered
    assert "Top-10 concentration: —" in rendered
    assert "Runtime dependency missing" in rendered
