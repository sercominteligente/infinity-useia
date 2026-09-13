from __future__ import annotations

import re

import httpx


_LAUGH_PATTERNS = (
    re.compile(r"(?i)\b[k]{3,}\b"),
    re.compile(r"(?i)\bk(?:\s+k){2,}\b"),
)


def normalize_spoken_text(text: str) -> str:
    """Prepare display text for natural speech without changing chat content.

    Brazilian chat laughter such as ``kkkk`` is natural in text but most TTS
    engines pronounce the letters individually. Convert only the speech copy to
    a short laugh cue that the speech model can render conversationally.
    """

    spoken = text.strip()
    for pattern in _LAUGH_PATTERNS:
        spoken = pattern.sub("haha", spoken)
    return re.sub(r"\s{2,}", " ", spoken)


class OpenAITTSClient:
    """Small server-side client for OpenAI speech generation.

    The API key never leaves the backend. Browser clients receive only audio bytes.
    """

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str = "gpt-4o-mini-tts",
        voice: str = "cedar",
        speed: float = 1.05,
        instructions: str = "",
        timeout: float = 60.0,
    ) -> None:
        self.api_key = api_key.strip()
        self.base_url = base_url.rstrip("/")
        self.model = model.strip() or "gpt-4o-mini-tts"
        self.voice = voice.strip() or "cedar"
        self.speed = speed
        self.instructions = instructions.strip()
        self.timeout = timeout

    def synthesize(self, text: str) -> bytes:
        text = normalize_spoken_text(text)
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not configured")
        if not text:
            raise ValueError("speech text cannot be empty")
        if len(text) > 4096:
            raise ValueError("speech text exceeds the 4096 character API limit")

        payload: dict[str, object] = {
            "model": self.model,
            "voice": self.voice,
            "input": text,
            "response_format": "mp3",
            "speed": self.speed,
        }
        if self.instructions:
            payload["instructions"] = self.instructions

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                f"{self.base_url}/audio/speech",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

        if response.status_code >= 400:
            detail = "OpenAI speech request failed"
            try:
                body = response.json()
                message = body.get("error", {}).get("message") if isinstance(body, dict) else None
                if message:
                    detail = f"{detail}: {message}"
            except Exception:
                pass
            raise RuntimeError(detail)

        if not response.content:
            raise RuntimeError("OpenAI speech request returned empty audio")
        return response.content
