import src.analyzers.audit_analysis as audit_analysis
from src.services.live_extractors import extract_audit_context


class DummyService:
    def __init__(self, payload):
        self.payload = payload

    def get_audit_context(self, symbol: str):
        return self.payload


def test_analyze_audit_marks_limited_validity_when_payload_is_partial():
    old_service = audit_analysis.get_market_data_service
    audit_analysis.get_market_data_service = lambda: DummyService({
        'symbol': 'BNB',
        'display_name': 'BNB',
        'audit_gate': 'WARN',
        'blocked_reason': 'Audit coverage is partial or unavailable.',
        'audit_summary': 'No live audit payload available in mock mode.',
        'risk_level': 'Medium',
        'audit_flags': [],
        'major_risks': [],
        'has_result': False,
        'is_supported': False,
    })
    try:
        brief = audit_analysis.analyze_audit('BNB')
    finally:
        audit_analysis.get_market_data_service = old_service

    assert brief.entity == 'Audit: BNB'
    assert any(tag.name == 'Audit Validity' and tag.level == 'Limited' for tag in brief.risk_tags)
    assert 'limited audit visibility' in brief.quick_verdict.lower()


def test_analyze_audit_marks_valid_supported_payload():
    old_service = audit_analysis.get_market_data_service
    audit_analysis.get_market_data_service = lambda: DummyService({
        'symbol': 'BNB',
        'display_name': 'BNB',
        'audit_gate': 'ALLOW',
        'audit_summary': 'Risk level 0 (LOW)',
        'risk_level': 'Low',
        'audit_flags': [],
        'major_risks': [],
        'has_result': True,
        'is_supported': True,
    })
    try:
        brief = audit_analysis.analyze_audit('BNB')
    finally:
        audit_analysis.get_market_data_service = old_service

    assert any(tag.name == 'Audit Validity' and tag.level == 'Valid' for tag in brief.risk_tags)


def test_analyze_audit_respects_validity_flags_from_extracted_live_payload():
    raw = {
        "query-token-info": {"metadata": {"symbol": "BNB", "name": "BNB"}},
        "query-token-audit": {"data": {"hasResult": True, "isSupported": True, "riskLevel": 1, "riskLevelEnum": "LOW", "riskItems": []}},
    }
    extracted = extract_audit_context(raw, "BNB")
    old_service = audit_analysis.get_market_data_service
    audit_analysis.get_market_data_service = lambda: DummyService(extracted)
    try:
        brief = audit_analysis.analyze_audit("BNB")
    finally:
        audit_analysis.get_market_data_service = old_service

    assert any(tag.name == "Audit Validity" and tag.level == "Valid" for tag in brief.risk_tags)
