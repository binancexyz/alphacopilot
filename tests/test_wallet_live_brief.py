from src.analyzers.wallet_live_brief import build_wallet_brief
from src.models.context import WalletContext


def test_build_wallet_brief():
    ctx = WalletContext(
        address="0x123",
        top_concentration_pct=72.0,
        notable_exposures=["meme", "AI"],
        major_risks=["Low diversification can amplify drawdowns."],
    )
    brief = build_wallet_brief(ctx)
    assert brief.entity == "Wallet: 0x123"
    assert brief.conviction is not None
    assert any(tag.name == "Evidence Quality" for tag in brief.risk_tags)
