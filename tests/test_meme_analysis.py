import src.analyzers.meme_analysis as meme_analysis


def test_analyze_meme_includes_evidence_quality():
    class DummyService:
        def get_meme_context(self, symbol: str):
            return {
                "symbol": symbol,
                "display_name": symbol,
                "signal_status": "unknown",
                "market_rank_context": "",
                "smart_money_count": 0,
                "signal_freshness": "UNKNOWN",
                "major_risks": [],
                "lifecycle_stage": "unknown",
                "launch_platform": "",
                "social_brief": "",
                "meme_score": 0,
                "top_holder_concentration_pct": 0,
            }

    old = meme_analysis.get_market_data_service
    meme_analysis.get_market_data_service = lambda: DummyService()
    try:
        brief = meme_analysis.analyze_meme("DOGE")
    finally:
        meme_analysis.get_market_data_service = old
    assert brief.entity == "Meme: DOGE"
    assert any(tag.name == "Evidence Quality" for tag in brief.risk_tags)
