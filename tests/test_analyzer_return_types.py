from src.analyzers.market_watch import watch_today
from src.analyzers.signal_check import analyze_signal
from src.analyzers.token_analysis import analyze_token
from src.analyzers.wallet_analysis import analyze_wallet
from src.models.schemas import AnalysisBrief


def test_analyzers_return_analysis_brief_instances():
    assert isinstance(analyze_token("BNB"), AnalysisBrief)
    assert isinstance(analyze_signal("DOGE"), AnalysisBrief)
    assert isinstance(analyze_wallet("0x123"), AnalysisBrief)
    assert isinstance(watch_today(), AnalysisBrief)
