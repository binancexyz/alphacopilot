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

def test_analyze_audit_pulls_bonding_curve_data_from_meme_lens():
    import src.analyzers.audit_analysis as audit_analysis
    from src.models.schemas import AnalysisBrief, RiskTag
    
    # Mock meme analyzer to return a valid meme brief with bonding progress
    def mock_analyze_meme(symbol: str):
        return AnalysisBrief(
            entity=f"Meme: {symbol}",
            quick_verdict="Valid meme candidate",
            signal_quality="High",
            risk_tags=[
                 RiskTag(name="Participation Quality", level="High", note="Active"),
                 RiskTag(name="Lifecycle", level="High", note="finalizing"),
                 RiskTag(name="Bonding Progress", level="High", note="95.5%"),
            ]
        )
    
    old_meme_analyzer = audit_analysis.analyze_meme
    audit_analysis.analyze_meme = mock_analyze_meme
    
    old_service = audit_analysis.get_market_data_service
    audit_analysis.get_market_data_service = lambda: DummyService({
        'symbol': 'PEPE',
        'display_name': 'PEPE',
        'audit_gate': 'ALLOW',
        'audit_summary': 'Risk level 0 (LOW)',
        'risk_level': 'Low',
        'audit_flags': [],
        'major_risks': [],
        'has_result': True,
        'is_supported': True,
    })
    
    try:
        brief = audit_analysis.analyze_audit('PEPE')
    finally:
        audit_analysis.analyze_meme = old_meme_analyzer
        audit_analysis.get_market_data_service = old_service

    # Check that Meme Lens was added
    assert any(section.title == "🧪 Meme Lens" for section in brief.sections)
    meme_section = next(section for section in brief.sections if section.title == "🧪 Meme Lens")
    
    # Check that Bonding Progress made it into the text
    assert "Bonding Progress:" in meme_section.content
    assert "95.5%" in meme_section.content
