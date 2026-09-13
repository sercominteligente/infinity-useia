from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


DEFAULT_TTS_INSTRUCTIONS = (
    "Fale em português brasileiro com voz madura, serena e confiante. "
    "Use ritmo natural e conversacional, presença de mentor experiente, "
    "pausas curtas e boa energia. Evite soar como locutor ou leitura robótica. "
    "Quando o texto trouxer 'haha', faça uma risada breve e natural; não soletre nem pronuncie letra por letra."
)


@dataclass(frozen=True)
class Settings:
    model_provider: str
    model: str
    memory_db: str
    log_level: str
    ollama_base_url: str
    omniroute_base_url: str
    omniroute_api_key: str
    omniroute_model: str
    omniroute_compression: str
    openai_api_key: str
    openai_base_url: str
    openai_tts_model: str
    openai_tts_voice: str
    openai_tts_speed: float
    openai_tts_instructions: str
    abacus_routellm_api_key: str
    abacus_routellm_base_url: str
    abacus_council_models: tuple[str, ...]
    abacus_synthesis_model: str


def _csv_models(value: str) -> tuple[str, ...]:
    models: list[str] = []
    for raw in value.split(","):
        model = raw.strip()
        if model and model not in models:
            models.append(model)
    return tuple(models)


def _float_env(name: str, default: float, *, minimum: float, maximum: float) -> float:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be a number") from exc
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return value


def load_settings() -> Settings:
    load_dotenv()
    provider = os.getenv("HAKHAM_MODEL_PROVIDER", "ollama").strip().lower()

    omniroute_base_url = os.getenv(
        "OMNIROUTE_BASE_URL", "http://127.0.0.1:20128/v1"
    ).strip().rstrip("/") or "http://127.0.0.1:20128/v1"
    omniroute_api_key = os.getenv("OMNIROUTE_API_KEY", "").strip()
    omniroute_model = os.getenv("OMNIROUTE_MODEL", "auto").strip() or "auto"
    omniroute_compression = os.getenv("OMNIROUTE_COMPRESSION", "").strip()

    model = os.getenv("HAKHAM_MODEL", "").strip()
    if not model:
        if provider == "abacus":
            model = "route-llm"
        elif provider == "omniroute":
            model = omniroute_model
        else:
            model = "llama3.2"
    if provider == "omniroute" and os.getenv("OMNIROUTE_MODEL", "").strip() == "":
        omniroute_model = model

    memory_db = os.getenv("HAKHAM_MEMORY_DB", "data/hakham.db").strip()
    log_level = os.getenv("HAKHAM_LOG_LEVEL", "INFO").strip().upper() or "INFO"
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").strip()
    openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
    openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip().rstrip("/")
    openai_tts_model = os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts").strip() or "gpt-4o-mini-tts"
    openai_tts_voice = os.getenv("OPENAI_TTS_VOICE", "cedar").strip() or "cedar"
    openai_tts_speed = _float_env("OPENAI_TTS_SPEED", 1.05, minimum=0.25, maximum=4.0)
    openai_tts_instructions = os.getenv("OPENAI_TTS_INSTRUCTIONS", "").strip() or DEFAULT_TTS_INSTRUCTIONS
    abacus_routellm_api_key = os.getenv("ABACUS_ROUTELLM_API_KEY", "").strip()
    abacus_routellm_base_url = os.getenv(
        "ABACUS_ROUTELLM_BASE_URL", "https://routellm.abacus.ai/v1"
    ).strip()
    abacus_council_models = _csv_models(os.getenv("HAKHAM_COUNCIL_MODELS", ""))
    abacus_synthesis_model = os.getenv("HAKHAM_COUNCIL_SYNTHESIS_MODEL", "route-llm").strip() or "route-llm"

    if provider not in {"ollama", "openai", "abacus", "omniroute"}:
        raise ValueError(f"unsupported HAKHAM_MODEL_PROVIDER: {provider}")

    return Settings(
        model_provider=provider,
        model=model,
        memory_db=memory_db,
        log_level=log_level,
        ollama_base_url=ollama_base_url,
        omniroute_base_url=omniroute_base_url,
        omniroute_api_key=omniroute_api_key,
        omniroute_model=omniroute_model,
        omniroute_compression=omniroute_compression,
        openai_api_key=openai_api_key,
        openai_base_url=openai_base_url,
        openai_tts_model=openai_tts_model,
        openai_tts_voice=openai_tts_voice,
        openai_tts_speed=openai_tts_speed,
        openai_tts_instructions=openai_tts_instructions,
        abacus_routellm_api_key=abacus_routellm_api_key,
        abacus_routellm_base_url=abacus_routellm_base_url,
        abacus_council_models=abacus_council_models,
        abacus_synthesis_model=abacus_synthesis_model,
    )
