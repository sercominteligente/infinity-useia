from hakham.core import HakhamCore
from hakham.memory import MemoryStore
from hakham.models import ModelProvider, ModelRouter


class FakeProvider(ModelProvider):
    def __init__(self):
        self.prompts = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return "Stored and understood."


def test_core_persists_exchange_and_reuses_context(tmp_path):
    db_path = tmp_path / "hakham.db"
    provider = FakeProvider()
    router = ModelRouter()
    router.register("fake", provider)
    core = HakhamCore(router, MemoryStore(str(db_path)), "fake")

    first = core.ask("SERhub is our ERP project.")
    assert first == "Stored and understood."

    restarted = HakhamCore(router, MemoryStore(str(db_path)), "fake")
    restarted.ask("What do you remember?")

    assert "SERhub is our ERP project." in provider.prompts[-1]


def test_core_exposes_verified_runtime_engine_metadata(tmp_path):
    provider = FakeProvider()
    router = ModelRouter()
    router.register("abacus", provider)
    core = HakhamCore(
        router,
        MemoryStore(str(tmp_path / "hakham.db")),
        "abacus",
        model="gpt-6-astra",
    )

    core.ask("Qual motor você está usando?")

    prompt = provider.prompts[-1]
    assert "provider configurado: abacus" in prompt
    assert "motor/modelo configurado: gpt-6-astra" in prompt
    assert "identidade do assistente: HAKHAM Infinity" in prompt


def test_router_refuses_unknown_provider():
    router = ModelRouter()
    try:
        router.generate("missing", "hello")
    except ValueError as exc:
        assert "unknown model provider" in str(exc)
    else:
        raise AssertionError("router should reject an unknown provider")
