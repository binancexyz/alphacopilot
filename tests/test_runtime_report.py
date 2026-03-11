from src.models.schemas import AnalysisBrief
from src.services.runtime_report import apply_runtime_meta, build_runtime_meta


def test_build_runtime_meta_mock_mode_shape():
    meta = build_runtime_meta('token', 'BNB')
    assert meta['mode'] in {'mock', 'live'}
    assert 'state' in meta


def test_apply_runtime_meta_adds_warning_to_brief():
    brief = AnalysisBrief(entity='Token: BNB', quick_verdict='x', signal_quality='Low')
    updated = apply_runtime_meta(brief, {'state': 'live_degraded', 'warning': 'Live runtime is degraded.'})
    assert updated.runtime_state == 'live_degraded'
    assert updated.runtime_warning == 'Live runtime is degraded.'
    assert updated.top_risks[0] == 'Live runtime is degraded.'
