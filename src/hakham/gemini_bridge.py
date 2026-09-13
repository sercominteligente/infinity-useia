from __future__ import annotations

import base64
import os
from typing import Any
from urllib.parse import quote

import httpx
from dotenv import load_dotenv

from .vision import VisionService as OpenAIVisionService
from .web_research import WebHit, WebResearchService


def _candidate_text(payload: dict[str, Any]) -> str:
    chunks: list[str] = []
    candidates = payload.get("candidates", [])
    if not isinstance(candidates, list):
        return ""
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        content = candidate.get("content", {})
        if not isinstance(content, dict):
            continue
        parts = content.get("parts", [])
        if not isinstance(parts, list):
            continue
        for part in parts:
            if not isinstance(part, dict):
                continue
            text = part.get("text")
            if isinstance(text, str) and text.strip():
                chunks.append(text.strip())
    return "\n".join(chunks).strip()


class GeminiVisionClient:
    """Direct Gemini multimodal sensor, without an SDK dependency."""

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-3.8-flash",
        base_url: str = "https://generativelanguage.googleapis.com/v1beta",
        timeout: float = 120.0,
    ) -> None:
        self.api_key = api_key.strip()
        self.model = model.strip() or "gemini-3.8-flash"
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    def analyze(self, image_bytes: bytes, mime_type: str, *, context: str = "") -> str:
        if not self.configured:
            raise ValueError("GEMINI_API_KEY is required for Gemini visual analysis")
        if not image_bytes:
            raise ValueError("empty image")

        encoded = base64.b64encode(image_bytes).decode("ascii")
        context_line = f"Contexto informado pelo Ach: {context.strip()}\n" if context.strip() else ""
        prompt = (
            "Você é o sensor visual do HAKHAM Infinity. Analise a imagem recebida agora. "
            "Responda em português do Brasil, de forma factual e útil. Leia textos visíveis quando possível, "
            "descreva interface, objetos, composição, cores, erros, produtos ou elementos relevantes. "
            "Quando houver incerteza, deixe explícito que é hipótese. Não invente detalhes. "
            "Não identifique pessoas desconhecidas nem infira atributos sensíveis.\n"
            f"{context_line}"
            "Finalize com uma linha iniciada por 'Chaves de memória:' com termos curtos para recuperação futura."
        )
        url = f"{self.base_url}/models/{quote(self.model, safe='')}:generateContent"
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                url,
                headers={"x-goog-api-key": self.api_key, "Content-Type": "application/json"},
                json={
                    "contents": [
                        {
                            "role": "user",
                            "parts": [
                                {"inline_data": {"mime_type": mime_type, "data": encoded}},
                                {"text": prompt},
                            ],
                        }
                    ],
                    "generationConfig": {"temperature": 0.15},
                },
            )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("invalid Gemini vision response")
        text = _candidate_text(payload)
        if not text:
            raise ValueError("Gemini vision response did not contain text")
        return text


class HybridVisionService(OpenAIVisionService):
    """Prefer Gemini for images while retaining the existing OpenAI sensor as fallback."""

    def __init__(self) -> None:
        super().__init__()
        load_dotenv()

        requested = os.getenv("HAKHAM_VISION_PROVIDER", "auto").strip().casefold() or "auto"
        gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        gemini_model = os.getenv("HAKHAM_GEMINI_VISION_MODEL", "gemini-3.8-flash").strip() or "gemini-3.8-flash"
        gemini_base = os.getenv(
            "GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta"
        ).strip() or "https://generativelanguage.googleapis.com/v1beta"

        self.provider = "openai"
        if requested not in {"auto", "gemini", "openai"}:
            requested = "auto"

        if requested in {"auto", "gemini"} and gemini_key:
            self.client = GeminiVisionClient(gemini_key, gemini_model, gemini_base)
            self.provider = "gemini"
        elif requested == "gemini":
            self.client = GeminiVisionClient("", gemini_model, gemini_base)
            self.provider = "gemini"


class GeminiWebResearchService(WebResearchService):
    """Use Gemini Google Search grounding first, then preserve the existing fallbacks."""

    def __init__(self, timeout: float = 20.0) -> None:
        super().__init__(timeout=timeout)
        load_dotenv()

        self.gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.gemini_model = (
            os.getenv("HAKHAM_GEMINI_SEARCH_MODEL", "gemini-3.8-flash").strip()
            or "gemini-3.8-flash"
        )
        self.gemini_base_url = (
            os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta").strip().rstrip("/")
            or "https://generativelanguage.googleapis.com/v1beta"
        )
        self.web_provider = os.getenv("HAKHAM_WEB_PROVIDER", "auto").strip().casefold() or "auto"
        self._real_abacus_key = self.abacus_key
        if self.web_provider in {"auto", "gemini"} and self.gemini_key and not self.abacus_key:
            self.abacus_key = "__gemini_grounding__"

    @property
    def gemini_search_ready(self) -> bool:
        return bool(self.gemini_key) and self.web_provider in {"auto", "gemini"}

    def _search_abacus(self, queries: list[str]) -> list[WebHit]:
        if self.gemini_search_ready:
            try:
                hits = self._search_gemini_google(queries)
                if hits:
                    return hits
            except Exception:
                if not self._real_abacus_key:
                    raise

        if self._real_abacus_key:
            current = self.abacus_key
            try:
                self.abacus_key = self._real_abacus_key
                return super()._search_abacus(queries)
            finally:
                self.abacus_key = current
        return []

    def _search_gemini_google(self, queries: list[str]) -> list[WebHit]:
        query = (queries[0] if queries else "").strip()
        if not query:
            return []

        prompt = (
            "Pesquise a Web atual usando Google Search para responder à missão abaixo. "
            "Priorize fontes primárias e confiáveis. Produza uma síntese factual curta em português do Brasil. "
            "Não invente fatos e mantenha as fontes retornadas pelo grounding.\n\n"
            f"Missão: {query}"
        )
        url = f"{self.gemini_base_url}/models/{quote(self.gemini_model, safe='')}:generateContent"
        with httpx.Client(timeout=max(self.timeout, 45.0), follow_redirects=True) as client:
            response = client.post(
                url,
                headers={"x-goog-api-key": self.gemini_key, "Content-Type": "application/json"},
                json={
                    "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                    "tools": [{"google_search": {}}],
                    "generationConfig": {"temperature": 0.15},
                },
            )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            return []

        summary = _candidate_text(payload)
        candidates = payload.get("candidates", [])
        chunks: list[dict[str, Any]] = []
        if isinstance(candidates, list):
            for candidate in candidates:
                if not isinstance(candidate, dict):
                    continue
                metadata = candidate.get("groundingMetadata") or candidate.get("grounding_metadata") or {}
                if not isinstance(metadata, dict):
                    continue
                rows = metadata.get("groundingChunks") or metadata.get("grounding_chunks") or []
                if isinstance(rows, list):
                    chunks.extend(row for row in rows if isinstance(row, dict))

        hits: list[WebHit] = []
        for row in chunks:
            web = row.get("web")
            if not isinstance(web, dict):
                continue
            url_value = str(web.get("uri") or web.get("url") or "").strip()
            title = str(web.get("title") or url_value).strip()
            if not url_value.startswith(("http://", "https://")):
                continue
            hits.append(
                WebHit(
                    title=title or url_value,
                    url=url_value,
                    snippet=summary[:1200] if not hits and summary else "",
                    content=summary[:5000] if not hits and summary else "",
                    provider="gemini-google-search",
                )
            )
        return self._dedupe_hits(hits)

    def _format_context(
        self,
        message: str,
        queries: list[str],
        hits: list[WebHit],
        provider: str,
        abacus_error: str,
    ) -> str:
        if any(hit.provider == "gemini-google-search" for hit in hits):
            provider = "gemini-google-search"
            abacus_error = ""
        return super()._format_context(message, queries, hits, provider, abacus_error)

    def search(self, query: str, max_results: int | None = None) -> dict[str, object]:
        if not self.gemini_search_ready:
            return super().search(query, max_results=max_results)

        query = query.strip()
        if not query:
            raise ValueError("web search query is required")
        limit = self.max_results if max_results is None else max(1, min(int(max_results), 12))
        try:
            hits = self._search_gemini_google(self.build_queries(query) or [query])
        except Exception:
            return super().search(query, max_results=max_results)
        if not hits:
            return super().search(query, max_results=max_results)
        return {
            "query": query,
            "provider": "gemini-google-search",
            "items": [hit.as_dict() for hit in hits[:limit]],
            "context_preview": self._format_context(
                query, self.build_queries(query) or [query], hits[:limit], "gemini-google-search", ""
            )[:4000],
        }
