from src.formatters.brief_formatter import format_brief
from src.models.schemas import AnalysisBrief, RiskTag


def test_format_signal_card_keeps_setup_structure_when_thin():
    brief = AnalysisBrief(
        entity="Signal: DOGE",
        quick_verdict="Watchlist only. Needs confirmation.",
        signal_quality="Low",
        top_risks=["Live signal confirmation is still too thin to treat this as a strong setup."],
        audit_gate="WARN",
    )
    rendered = format_brief(brief)
    assert "⚡ Setup" in rendered
    assert "Entry zone: — limited" in rendered
    assert "Signal age: — limited" in rendered
    assert "Invalidation: Needs confirmation" in rendered or "Invalidation: Thin payload" in rendered



def test_format_token_card_keeps_ownership_structure_when_thin():
    brief = AnalysisBrief(
        entity="Token: BNB",
        quick_verdict="Thin read. No conviction yet.",
        signal_quality="Low",
        top_risks=["Too much live token context is still missing, so this read should stay provisional."],
        why_it_matters="",
        audit_gate="WARN",
    )
    rendered = format_brief(brief)
    assert "⚡ Snapshot" in rendered
    assert "💼 Ownership" in rendered
    assert "Holders: —" in rendered
    assert "Smart money: —" in rendered
    assert "Liquidity: — limited" in rendered



def test_format_watchtoday_card_keeps_sections_when_thin():
    brief = AnalysisBrief(
        entity="Market Watch",
        quick_verdict="Quiet board. Hold posture.",
        signal_quality="Low",
        top_risks=["Too many daily market lanes are still sparse, so this board should be treated as lower-confidence."],
    )
    rendered = format_brief(brief)
    assert "⚡ Signals" in rendered
    assert "No clean board leader yet" in rendered
    assert "🔥 Attention" in rendered
    assert "Attention is limited" in rendered
    assert "Sparse lane coverage" in rendered



def test_format_audit_card_surfaces_limited_validity():
    brief = AnalysisBrief(
        entity="Audit: BNB",
        quick_verdict="BNB|BNB|Medium|No live audit payload available in mock mode.|Contract: —|Liquidity: Partial visibility ⚠️|Structure: Partial|warn|Limited audit visibility. Stay cautious.",
        signal_quality="Medium",
        risk_tags=[RiskTag(name="Audit Validity", level="Limited", note="Live audit validity is partial or unsupported right now.")],
        audit_gate="WARN",
    )
    rendered = format_brief(brief)
    assert "Limited audit visibility" in rendered
