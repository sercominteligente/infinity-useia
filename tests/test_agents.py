import pytest

from hakham.agents import AgentRegistry


def test_default_agent_team_contains_orchestrator_and_specialists():
    registry = AgentRegistry()
    ids = {agent.id for agent in registry.all()}

    assert "hakham" in ids
    assert {"serafim", "arcanum", "delta", "luna", "ser-master"}.issubset(ids)
    assert registry.get("hakham").role == "orchestrator"


def test_specialist_prompt_preserves_identity_and_task():
    registry = AgentRegistry()
    prompt = registry.prompt_for("serafim", "Revise a arquitetura do painel")

    assert "Serafim Web" in prompt
    assert "Revise a arquitetura do painel" in prompt
    assert "Não diga que executou ferramentas" in prompt


def test_unknown_agent_is_rejected():
    with pytest.raises(ValueError, match="unknown agent"):
        AgentRegistry().prompt_for("fantasma", "teste")
