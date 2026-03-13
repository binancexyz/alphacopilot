from src.formatters.brief_formatter import format_brief
from src.models.schemas import AnalysisBrief, RiskTag


def test_wallet_thin_state_keeps_premium_structure():
    brief = AnalysisBrief(
        entity="Wallet: 0x1234567890abcdef",
        quick_verdict="Too thin to read. Return after rotation activity.",
        signal_quality="Low",
        top_risks=["Current live wallet context is too thin to support a strong behavior judgment."],
        risk_tags=[RiskTag(name="Follow Verdict", level="Medium", note="Unknown")],
    )
    rendered = format_brief(brief)
    assert "**⚡ Behavior**" in rendered
    assert "Activity: Limited" in rendered
    assert "Top move: No rotation visible" in rendered
    assert "Drift: Follow signal unavailable" in rendered
    assert "**⚠️ Thin payload · Not a follow signal**" in rendered



def test_portfolio_unavailable_state_keeps_holdings_block():
    brief = AnalysisBrief(
        entity="Portfolio: Binance Spot",
        quick_verdict="Portfolio read is unavailable right now.",
        signal_quality="Unavailable",
        top_risks=["httpx is required for Binance account reads."],
        why_it_matters="This command is read-only, but it still depends on valid Binance API credentials and account-read permission.",
    )
    rendered = format_brief(brief)
    assert "**⚡ Posture**" in rendered
    assert "**💼 Top Holdings**" in rendered
    assert "No priced holdings visible" in rendered
    assert "Read-only snapshot unavailable" in rendered
    assert "Runtime dependency missing" in rendered or "Read-only estimate" in rendered
