import pytest

from hakham.council import ModelCouncil


class FakeRouteProvider:
    def __init__(self):
        self.calls = []

    def generate_with_model(self, prompt: str, model: str) -> str:
        self.calls.append((model, prompt))
        return f"answer from {model}"


def test_council_requires_two_distinct_models():
    council = ModelCouncil(FakeRouteProvider())
    with pytest.raises(ValueError):
        council.deliberate("question", models=["same", "same"])


def test_council_is_bounded_and_synthesizes():
    provider = FakeRouteProvider()
    council = ModelCouncil(provider, max_members=3)

    result = council.deliberate(
        "Which architecture should we use?",
        models=["model-a", "model-b", "model-c", "model-d"],
        synthesis_model="route-llm",
    )

    assert [voice.model for voice in result.voices] == ["model-a", "model-b", "model-c"]
    assert result.synthesis_model == "route-llm"
    assert result.synthesis == "answer from route-llm"
    assert [call[0] for call in provider.calls] == ["model-a", "model-b", "model-c", "route-llm"]
    assert "Never invent consensus" in provider.calls[-1][1]
