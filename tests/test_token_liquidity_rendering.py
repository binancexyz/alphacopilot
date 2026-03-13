from src.analyzers.token_live_brief import build_token_brief
from src.formatters.brief_formatter import format_brief
from src.models.context import TokenContext


def test_token_render_uses_explicit_liquidity_tag_when_present():
    brief = build_token_brief(
        TokenContext(
            symbol='BNB',
            display_name='BNB',
            price=667.55,
            liquidity=59300000,
            holders=0,
            signal_status='unmatched',
            audit_gate='ALLOW',
        )
    )
    rendered = format_brief(brief)
    assert 'Liquidity: $59.3M' in rendered
