import src.analyzers.audit_analysis as audit_analysis


class DummyService:
    def __init__(self, payload):
        self.payload = payload

    def get_audit_context(self, symbol: str):
        return self.payload



def test_audit_marks_blocked_structural_risk():
    old_service = audit_analysis.get_market_data_service
    audit_analysis.get_market_data_service = lambda: DummyService({
        'symbol': 'DOGE',
        'display_name': 'DOGE',
        'audit_gate': 'BLOCK',
        'blocked_reason': 'Critical audit flags detected.',
        'audit_summary': 'Risk level 5 (HIGH)',
        'risk_level': 'High',
        'audit_flags': ['Risk level 5 (HIGH)', 'Sell tax above 10%'],
        'major_risks': ['SCAM_RISK: Honeypot risk detected.'],
        'has_result': True,
        'is_supported': True,
    })
    try:
        brief = audit_analysis.analyze_audit('DOGE')
    finally:
        audit_analysis.get_market_data_service = old_service

    assert 'Avoid. Structural risk is too high.' in brief.quick_verdict
    assert '|High|' in brief.quick_verdict
    assert 'Contract: Critical audit flags detected.' in brief.quick_verdict



def test_audit_marks_tax_heavy_as_tradable_but_flagged():
    old_service = audit_analysis.get_market_data_service
    audit_analysis.get_market_data_service = lambda: DummyService({
        'symbol': 'DOGE',
        'display_name': 'DOGE',
        'audit_gate': 'WARN',
        'audit_summary': 'Risk level 2 (MEDIUM); Sell tax above 10%',
        'risk_level': 'Medium',
        'audit_flags': ['Sell tax above 10%'],
        'major_risks': ['TRADE_RISK: Sell tax above 10%.'],
        'has_result': True,
        'is_supported': True,
    })
    try:
        brief = audit_analysis.analyze_audit('DOGE')
    finally:
        audit_analysis.get_market_data_service = old_service

    assert 'Tradable but flagged. Tax friction is high.' in brief.quick_verdict
    assert 'Liquidity: Sell tax above 10%' in brief.quick_verdict



def test_audit_does_not_imply_clean_when_result_is_unsupported():
    old_service = audit_analysis.get_market_data_service
    audit_analysis.get_market_data_service = lambda: DummyService({
        'symbol': 'DOGE',
        'display_name': 'DOGE',
        'audit_gate': 'WARN',
        'blocked_reason': 'Audit coverage is partial or unavailable.',
        'audit_summary': 'Audit payload unavailable.',
        'risk_level': 'Low',
        'audit_flags': [],
        'major_risks': [],
        'has_result': False,
        'is_supported': False,
    })
    try:
        brief = audit_analysis.analyze_audit('DOGE')
    finally:
        audit_analysis.get_market_data_service = old_service

    assert 'Limited audit visibility. Stay cautious.' in brief.quick_verdict
    assert 'Contract: Partial visibility' in brief.quick_verdict
    assert any(tag.name == 'Audit Validity' and tag.level == 'Limited' for tag in brief.risk_tags)
