import pytest

from hakham.ignite import build_provider


def test_build_provider_uses_abacus_env(monkeypatch):
    monkeypatch.setenv("HAKHAM_MODEL_PROVIDER", "abacus")
    monkeypatch.setenv("HAKHAM_MODEL", "route-llm")
    monkeypatch.setenv("ABACUS_ROUTELLM_API_KEY", "test-key")
    monkeypatch.setenv("ABACUS_ROUTELLM_BASE_URL", "https://example.invalid/v1")

    provider = build_provider()

    assert provider.model == "route-llm"
    assert provider.base_url == "https://example.invalid/v1"


def test_build_provider_refuses_non_abacus_provider(monkeypatch):
    monkeypatch.setenv("HAKHAM_MODEL_PROVIDER", "ollama")
    monkeypatch.delenv("ABACUS_ROUTELLM_API_KEY", raising=False)

    with pytest.raises(ValueError):
        build_provider()
