from __future__ import annotations

import logging
from abc import ABC, abstractmethod

import httpx


logger = logging.getLogger(__name__)


class ModelProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        raise NotImplementedError


class OllamaProvider(ModelProvider):
    def __init__(self, model: str, base_url: str = "http://localhost:11434") -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt: str) -> str:
        logger.info("model_call provider=ollama model=%s", self.model)
        response = httpx.post(
            f"{self.base_url}/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": False},
            timeout=120,
        )
        response.raise_for_status()
        return response.json()["response"].strip()


class OpenAIProvider(ModelProvider):
    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str = "https://api.openai.com/v1",
    ) -> None:
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for the OpenAI provider")
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt: str) -> str:
        logger.info("model_call provider=openai model=%s", self.model)
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=120,
        )
        response.raise_for_status()
        payload = response.json()
        return payload["choices"][0]["message"]["content"].strip()


class RouteLLMProvider(ModelProvider):
    """Abacus.AI RouteLLM propulsion provider.

    HAKHAM keeps identity, memory, policy and orchestration locally. This
    provider only executes the minimum prompt needed against a replaceable
    external model endpoint.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "route-llm",
        base_url: str = "https://routellm.abacus.ai/v1",
    ) -> None:
        if not api_key:
            raise ValueError("ABACUS_ROUTELLM_API_KEY is required for the Abacus provider")
        self.api_key = api_key
        self.model = model or "route-llm"
        self.base_url = base_url.rstrip("/")

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _generate(self, prompt: str, *, model: str) -> str:
        logger.info("model_call provider=abacus model=%s", model)
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers=self._headers,
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=120,
        )
        response.raise_for_status()
        payload = response.json()
        try:
            content = payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError("invalid RouteLLM response: missing assistant content") from exc
        if not isinstance(content, str) or not content.strip():
            raise ValueError("invalid RouteLLM response: empty assistant content")
        return content.strip()

    def generate(self, prompt: str) -> str:
        return self._generate(prompt, model=self.model)

    def generate_with_model(self, prompt: str, model: str) -> str:
        model = model.strip()
        if not model:
            raise ValueError("model is required")
        return self._generate(prompt, model=model)

    def list_models(self) -> list[dict[str, object]]:
        logger.info("catalog_call provider=abacus")
        response = httpx.get(
            f"{self.base_url}/models",
            headers=self._headers,
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        data = payload.get("data", []) if isinstance(payload, dict) else []
        if not isinstance(data, list):
            raise ValueError("invalid RouteLLM models response")
        return [item for item in data if isinstance(item, dict)]

    def health(self) -> dict[str, object]:
        """Validate authentication/catalog access without spending a text-generation call."""
        models = self.list_models()
        result = {
            "provider": "abacus",
            "ok": True,
            "base_url": self.base_url,
            "configured_model": self.model,
            "model_count": len(models),
        }
        logger.info("health_check provider=abacus ok=true model_count=%s", len(models))
        return result


class OmniRouteProvider(ModelProvider):
    """Local-first OpenAI-compatible gateway used as HAKHAM's economy engine.

    OmniRoute can run without an API key on localhost. When a key is configured
    HAKHAM sends it as a Bearer token. The provider records only non-secret
    routing/compression response metadata so the UI can explain which path won.
    """

    def __init__(
        self,
        model: str = "auto",
        base_url: str = "http://127.0.0.1:20128/v1",
        api_key: str = "",
        compression: str = "",
        timeout: float = 120.0,
    ) -> None:
        self.model = model.strip() or "auto"
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key.strip()
        self.compression = compression.strip()
        self.timeout = timeout
        self.last_decision = ""
        self.last_compression = ""

    @property
    def configured(self) -> bool:
        return bool(self.base_url)

    @property
    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        if self.compression:
            headers["X-OmniRoute-Compression"] = self.compression
        return headers

    @staticmethod
    def _assistant_text(payload: dict[str, object]) -> str:
        choices = payload.get("choices", [])
        if not isinstance(choices, list) or not choices:
            raise ValueError("invalid OmniRoute response: missing choices")
        first = choices[0]
        if not isinstance(first, dict):
            raise ValueError("invalid OmniRoute response: invalid choice")
        message = first.get("message", {})
        if not isinstance(message, dict):
            raise ValueError("invalid OmniRoute response: missing message")
        content = message.get("content", "")
        if isinstance(content, str) and content.strip():
            return content.strip()
        if isinstance(content, list):
            chunks: list[str] = []
            for part in content:
                if not isinstance(part, dict):
                    continue
                text = part.get("text")
                if isinstance(text, str) and text.strip():
                    chunks.append(text.strip())
            if chunks:
                return "\n".join(chunks)
        raise ValueError("invalid OmniRoute response: empty assistant content")

    def _capture_metadata(self, response: httpx.Response) -> None:
        self.last_decision = response.headers.get("X-OmniRoute-Decision", "").strip()
        self.last_compression = response.headers.get("X-OmniRoute-Compression", "").strip()

    def generate(self, prompt: str) -> str:
        logger.info("model_call provider=omniroute model=%s", self.model)
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers=self._headers,
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=self.timeout,
        )
        self._capture_metadata(response)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("invalid OmniRoute response")
        return self._assistant_text(payload)

    def list_models(self) -> list[dict[str, object]]:
        response = httpx.get(
            f"{self.base_url}/models",
            headers=self._headers,
            timeout=30,
        )
        self._capture_metadata(response)
        response.raise_for_status()
        payload = response.json()
        data = payload.get("data", []) if isinstance(payload, dict) else []
        if not isinstance(data, list):
            raise ValueError("invalid OmniRoute models response")
        return [item for item in data if isinstance(item, dict)]

    def health(self) -> dict[str, object]:
        models = self.list_models()
        return {
            "provider": "omniroute",
            "ok": True,
            "base_url": self.base_url,
            "configured_model": self.model,
            "model_count": len(models),
            "auth_configured": bool(self.api_key),
            "compression": self.compression or "gateway-default",
        }

    def telemetry(self) -> dict[str, str]:
        return {
            "decision": self.last_decision,
            "compression": self.last_compression,
        }


class ModelRouter:
    """Explicit provider router. No silent cloud fallback."""

    def __init__(self) -> None:
        self._providers: dict[str, ModelProvider] = {}

    def register(self, name: str, provider: ModelProvider) -> None:
        self._providers[name] = provider

    def provider(self, name: str) -> ModelProvider:
        try:
            return self._providers[name]
        except KeyError as exc:
            raise ValueError(f"unknown model provider: {name}") from exc

    def generate(self, provider: str, prompt: str) -> str:
        return self.provider(provider).generate(prompt)
