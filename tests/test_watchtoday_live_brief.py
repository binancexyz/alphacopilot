from src.analyzers.watchtoday_live_brief import build_watchtoday_brief
from src.models.context import WatchTodayContext


def test_build_watchtoday_brief():
    ctx = WatchTodayContext(
        top_narratives=["AI", "meme rotation", "L2"],
        strongest_signals=["AI inflows", "BNB strength"],
        risk_zones=["overheated meme names"],
        market_takeaway="Opportunity exists, but selectivity matters.",
        major_risks=["Trending sectors may already be overheated."],
    )
    brief = build_watchtoday_brief(ctx)
    assert brief.entity == "Market Watch"
    assert brief.conviction is not None
