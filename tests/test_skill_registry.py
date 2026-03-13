from src.services.skill_registry import get_skill_reference


def test_skill_registry_resolves_query_token_info_reference():
    ref = get_skill_reference("query-token-info")
    assert ref is not None
    assert ref.name == "query-token-info"
    assert ref.version == "1.0"
    assert ref.source == "binance/binance-skills-hub"
    assert ref.path.endswith("/.agents/skills/query-token-info")
    assert any("token/search" in endpoint for endpoint in ref.endpoints)
    assert "binance-web3/1.0 (Skill)" in ref.user_agent
