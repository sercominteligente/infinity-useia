import httpx
import pytest

from hakham.models import RouteLLMProvider


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_routellm_requires_api_key():
    with pytest.raises(ValueError, match="ABACUS_ROUTELLM_API_KEY"):
        RouteLLMProvider(api_key="")


def test_routellm_generate_uses_openai_compatible_endpoint(monkeypatch):
    captured = {}

    def fake_post(url, *, headers, json, timeout):
        captured.update(url=url, headers=headers, json=json, timeout=timeout)
        return FakeResponse(
            {
                "choices": [
                    {"message": {"role": "assistant", "content": "Shalom, Ach!"}}
                ]
            }
        )

    monkeypatch.setattr(httpx, "post", fake_post)
    provider = RouteLLMProvider(api_key="test-key", model="route-llm")

    answer = provider.generate("Where do we attack today?")

    assert answer == "Shalom, Ach!"
    assert captured["url"] == "https://routellm.abacus.ai/v1/chat/completions"
    assert captured["headers"]["Authorization"] == "Bearer test-key"
    assert captured["json"]["model"] == "route-llm"
    assert captured["json"]["messages"][0]["role"] == "user"
    assert captured["timeout"] == 120


def test_routellm_rejects_empty_assistant_content(monkeypatch):
    def fake_post(url, *, headers, json, timeout):
        return FakeResponse({"choices": [{"message": {"content": ""}}]})

    monkeypatch.setattr(httpx, "post", fake_post)
    provider = RouteLLMProvider(api_key="test-key")

    with pytest.raises(ValueError, match="empty assistant content"):
        provider.generate("hello")


def test_routellm_lists_live_catalog_shape(monkeypatch):
    captured = {}

    def fake_get(url, *, headers, timeout):
        captured.update(url=url, headers=headers, timeout=timeout)
        return FakeResponse(
            {
                "object": "list",
                "data": [
                    {"id": "route-llm", "object": "model"},
                    {"id": "example-model", "object": "model"},
                ],
            }
        )

    monkeypatch.setattr(httpx, "get", fake_get)
    provider = RouteLLMProvider(api_key="test-key")

    models = provider.list_models()

    assert [item["id"] for item in models] == ["route-llm", "example-model"]
    assert captured["url"] == "https://routellm.abacus.ai/v1/models"
    assert captured["headers"]["Authorization"] == "Bearer test-key"
    assert captured["timeout"] == 30
