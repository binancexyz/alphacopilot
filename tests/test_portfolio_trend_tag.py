from src.models.schemas import RiskTag


def test_short_trend_tag_shape():
    tag = RiskTag(name='Short Trend', level='Info', note='visible value is up versus the older local trend')
    assert tag.name == 'Short Trend'
    assert tag.level == 'Info'
    assert 'older local trend' in (tag.note or '')
