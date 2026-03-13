from __future__ import annotations

from src.services.binance_skill_mapping import COMMAND_SKILL_MAP, OPTIONAL_COMMAND_SKILL_MAP


def test_all_commands_have_nonempty_skill_lists():
    for command, skills in COMMAND_SKILL_MAP.items():
        assert isinstance(skills, list), f"command={command} has non-list skills"
        assert len(skills) > 0, f"command={command} has empty skill list"


def test_optional_commands_are_valid():
    for command in OPTIONAL_COMMAND_SKILL_MAP:
        assert command in COMMAND_SKILL_MAP, f"optional command={command} is not in COMMAND_SKILL_MAP"


def test_alpha_command_exists():
    assert "alpha" in COMMAND_SKILL_MAP
    assert "alpha" in COMMAND_SKILL_MAP["alpha"]


def test_futures_command_exists():
    assert "futures" in COMMAND_SKILL_MAP
    assert "derivatives-trading-usds-futures" in COMMAND_SKILL_MAP["futures"]


def test_token_has_optional_enrichments():
    assert "token" in OPTIONAL_COMMAND_SKILL_MAP
    optional = OPTIONAL_COMMAND_SKILL_MAP["token"]
    assert "alpha" in optional
    assert "spot" in optional
    assert "derivatives-trading-usds-futures" in optional
