from src.analyzers.wallet_live_brief import build_wallet_brief
from src.models.context import WalletContext, WalletHolding


def test_build_wallet_brief():
    ctx = WalletContext(
        address="0x123",
        portfolio_value=125000,
        holdings_count=6,
        top_holdings=[WalletHolding(symbol="BNB", weight_pct=42.0)],
        top_concentration_pct=72.0,
        notable_exposures=["meme", "AI"],
        change_24h=4.5,
        major_risks=["Low diversification can amplify drawdowns."],
    )
    brief = build_wallet_brief(ctx)
    assert brief.entity == "Wallet: 0x123"
    assert brief.conviction is not None
    assert any(tag.name == "Evidence Quality" for tag in brief.risk_tags)
    assert any(tag.name == "Activity" for tag in brief.risk_tags)
    assert any(tag.name == "Style Profile" for tag in brief.risk_tags)
    assert "Current read:" in brief.why_it_matters
    assert "Behavior profile:" in brief.why_it_matters
