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
    assert any(tag.name == "Evidence Quality" for tag in brief.risk_tags)


def test_build_watchtoday_brief_includes_lane_coverage_when_partial():
    ctx = WatchTodayContext(
        top_narratives=["AI"],
        strongest_signals=["BNB strength"],
        market_takeaway="Opportunity exists, but selectivity matters.",
    )
    brief = build_watchtoday_brief(ctx)
    titles = [section.title for section in brief.sections]
    assert "🧩 Lane Coverage" in titles
    lane_section = next(section for section in brief.sections if section.title == "🧩 Lane Coverage")
    assert "Sparse:" in lane_section.content
    assert "selective rather than complete" in brief.quick_verdict or brief.conviction == "Low"
