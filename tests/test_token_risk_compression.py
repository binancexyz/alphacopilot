from src.formatters.brief_formatter import format_brief
from src.models.schemas import AnalysisBrief


def test_token_footer_compresses_user_reported_risk():
    brief = AnalysisBrief(
        entity='Token: BTC',
        quick_verdict='Monitor only. No signal match.',
        signal_quality='Low',
        top_risks=['Scam Risk: User Reported. This token has been reported as risky by users. It is recommended that you conduct further research to ensure security.'],
        audit_gate='WARN',
    )
    rendered = format_brief(brief)
    assert 'User-reported risk' in rendered



def test_token_footer_compresses_upgradeable_contract_risk():
    brief = AnalysisBrief(
        entity='Token: DOGE',
        quick_verdict='Monitor only. No signal match.',
        signal_quality='Low',
        top_risks=['Contract Risk: Contract Upgradeable. Upgradeable contract means the token contract can potentially change rules and may introduce malicious functions.'],
        audit_gate='WARN',
    )
    rendered = format_brief(brief)
    assert 'Upgradeable contract' in rendered
