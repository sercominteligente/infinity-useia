from hakham.config import load_settings


def test_abacus_provider_defaults_to_route_llm(monkeypatch):
    monkeypatch.setenv("HAKHAM_MODEL_PROVIDER", "abacus")
    monkeypatch.delenv("HAKHAM_MODEL", raising=False)
    monkeypatch.setenv("ABACUS_ROUTELLM_API_KEY", "test-key")
    monkeypatch.delenv("ABACUS_ROUTELLM_BASE_URL", raising=False)

    settings = load_settings()

    assert settings.model_provider == "abacus"
    assert settings.model == "route-llm"
    assert settings.abacus_routellm_api_key == "test-key"
    assert settings.abacus_routellm_base_url == "https://routellm.abacus.ai/v1"


def test_abacus_provider_allows_explicit_model(monkeypatch):
    monkeypatch.setenv("HAKHAM_MODEL_PROVIDER", "abacus")
    monkeypatch.setenv("HAKHAM_MODEL", "example-model")
    monkeypatch.setenv("ABACUS_ROUTELLM_API_KEY", "test-key")

    settings = load_settings()

    assert settings.model == "example-model"
