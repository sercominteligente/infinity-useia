from __future__ import annotations

import base64
import os
from typing import Any

import httpx
from dotenv import load_dotenv

from .gemini_bridge import GeminiVisionClient
from .vision import OpenAIVisionClient, VisionService


def _abacus_text(payload: dict[str, Any]) -> str:
    choices = payload.get("choices", [])
    if not isinstance(choices, list) or not choices:
        return ""
    first = choices[0]
    if not isinstance(first, dict):
        return ""
    message = first.get("message", {})
    if not isinstance(message, dict):
        return ""
    content = message.get("content", "")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        chunks: list[str] = []
        for part in content:
            if not isinstance(part, dict):
                continue
            text = part.get("text")
            if isinstance(text, str) and text.strip():
                chunks.append(text.strip())
        return "\n".join(chunks).strip()
    return ""


class AbacusVisionClient:
    """Vision through Abacus RouteLLM's OpenAI-compatible multimodal endpoint."""

    def __init__(
        self,
        api_key: str,
        model: str = "route-llm",
        base_url: str = "https://routellm.abacus.ai/v1",
        timeout: float = 120.0,
    ) -> None:
        self.api_key = api_key.strip()
        self.model = model.strip() or "route-llm"
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    def analyze(self, image_bytes: bytes, mime_type: str, *, context: str = "") -> str:
        if not self.configured:
            raise ValueError("ABACUS_ROUTELLM_API_KEY is required for RouteLLM visual analysis")
        if not image_bytes:
            raise ValueError("empty image")

        encoded = base64.b64encode(image_bytes).decode("ascii")
        context_line = f"Contexto informado pelo Ach: {context.strip()}\n" if context.strip() else ""
        prompt = (
            "Você é o sensor visual do HAKHAM Infinity. Analise a imagem recebida agora. "
            "Responda em português do Brasil, de forma factual, objetiva e útil. Leia textos visíveis quando possível, "
            "descreva interfaces, objetos, composição, cores, erros e detalhes relevantes. Diferencie observação de hipótese. "
            "Não identifique pessoas desconhecidas nem infira atributos sensíveis.\n"
            f"{context_line}"
            "Finalize com uma linha iniciada por 'Chaves de memória:' contendo termos curtos para recuperação futura."
        )
        data_url = f"data:{mime_type};base64,{encoded}"
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": data_url}},
                            ],
                        }
                    ],
                    "temperature": 0.15,
                    "max_tokens": 1800,
                },
            )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("invalid RouteLLM vision response")
        text = _abacus_text(payload)
        if not text:
            raise ValueError("RouteLLM vision response did not contain text")
        return text


class RoutedVisionClient:
    """Economy-first visual router with deterministic provider order and safe fallback."""

    def __init__(self, candidates: list[tuple[str, object]]) -> None:
        self.candidates = candidates
        self.last_provider = ""
        self.last_model = ""

    @property
    def configured(self) -> bool:
        return any(bool(getattr(client, "configured", False)) for _, client in self.candidates)

    @property
    def provider_chain(self) -> list[str]:
        return [name for name, client in self.candidates if bool(getattr(client, "configured", False))]

    @property
    def model(self) -> str:
        if self.last_model:
            return self.last_model
        configured = [
            f"{name}:{getattr(client, 'model', 'unknown')}"
            for name, client in self.candidates
            if bool(getattr(client, "configured", False))
        ]
        return " -> ".join(configured) if configured else "vision-unconfigured"

    def analyze(self, image_bytes: bytes, mime_type: str, *, context: str = "") -> str:
        errors: list[str] = []
        for provider, client in self.candidates:
            if not bool(getattr(client, "configured", False)):
                continue
            try:
                text = client.analyze(image_bytes, mime_type, context=context)
                self.last_provider = provider
                self.last_model = str(getattr(client, "model", "unknown"))
                return text
            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code if exc.response is not None else "HTTP"
                errors.append(f"{provider}:{status}")
            except httpx.HTTPError as exc:
                errors.append(f"{provider}:{type(exc).__name__}")
            except Exception as exc:
                errors.append(f"{provider}:{type(exc).__name__}")
        detail = ", ".join(errors) if errors else "nenhum provedor visual configurado"
        raise RuntimeError(f"todos os provedores visuais falharam ({detail})")


class EconomicalVisionService(VisionService):
    """Visual memory service using Gemini/RouteLLM first and OpenAI only by explicit choice."""

    def __init__(self) -> None:
        super().__init__()
        load_dotenv()

        requested = os.getenv("HAKHAM_VISION_PROVIDER", "auto").strip().casefold() or "auto"
        if requested not in {"auto", "gemini", "abacus", "openai"}:
            requested = "auto"

        gemini = GeminiVisionClient(
            os.getenv("GEMINI_API_KEY", ""),
            os.getenv("HAKHAM_GEMINI_VISION_MODEL", "gemini-3.8-flash"),
            os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta"),
        )
        abacus = AbacusVisionClient(
            os.getenv("ABACUS_ROUTELLM_API_KEY", ""),
            os.getenv("HAKHAM_ABACUS_VISION_MODEL", "route-llm"),
            os.getenv("ABACUS_ROUTELLM_BASE_URL", "https://routellm.abacus.ai/v1"),
        )
        openai = OpenAIVisionClient(
            os.getenv("OPENAI_API_KEY", ""),
            os.getenv("HAKHAM_VISION_MODEL", "gpt-5.6-luna"),
            os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        )

        allow_openai_fallback = os.getenv("HAKHAM_VISION_ALLOW_OPENAI_FALLBACK", "false").strip().casefold() in {
            "1",
            "true",
            "yes",
            "on",
        }

        if requested == "gemini":
            candidates = [("gemini", gemini)]
        elif requested == "abacus":
            candidates = [("abacus", abacus)]
        elif requested == "openai":
            candidates = [("openai", openai)]
        else:
            candidates = [("gemini", gemini), ("abacus", abacus)]
            if allow_openai_fallback:
                candidates.append(("openai", openai))

        self.client = RoutedVisionClient(candidates)
        self.provider = requested

    @property
    def active_provider(self) -> str:
        return self.client.last_provider or (self.client.provider_chain[0] if self.client.provider_chain else "unconfigured")
