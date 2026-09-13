import pytest
from fastapi.testclient import TestClient

from hakham import web as backend
from hakham.web_v4 import OpenAITTSClient, app


@pytest.fixture(autouse=True)
def reset_runtime_state():
    backend.runtime._runtime = None
    backend.runtime._fingerprint = None
    backend.runtime._mode = None
    yield
    backend.runtime._runtime = None
    backend.runtime._fingerprint = None
    backend.runtime._mode = None


def test_v4_home_exposes_fast_gpt_voice(monkeypatch, tmp_path):
    monkeypatch.setenv("HAKHAM_MODEL_PROVIDER", "ollama")
    monkeypatch.setenv("HAKHAM_MODEL", "llama3.2")
    monkeypatch.setenv("HAKHAM_MEMORY_DB", str(tmp_path / "hakham.db"))

    response = TestClient(app).get("/")

    assert response.status_code == 200
    assert "HAKHAM INFINITY ∞ v0.4.1" in response.text
    assert "GPT VOICE FAST" in response.text
    assert "/api/voice/speech" in response.text
    assert "splitHakhamSpeech" in response.text
    assert "fetchHakhamNaturalChunk" in response.text


def test_v4_status_hides_key_and_reports_tts(monkeypatch, tmp_path):
    monkeypatch.setenv("HAKHAM_MODEL_PROVIDER", "ollama")
    monkeypatch.setenv("HAKHAM_MODEL", "llama3.2")
    monkeypatch.setenv("HAKHAM_MEMORY_DB", str(tmp_path / "hakham.db"))
    monkeypatch.setenv("OPENAI_API_KEY", "super-secret-test-key")
    monkeypatch.setenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
    monkeypatch.setenv("OPENAI_TTS_VOICE", "cedar")

    payload = TestClient(app).get("/api/status").json()

    assert payload["version"] == "0.4.1"
    assert payload["voice_latency_mode"] == "fast"
    assert payload["openai_tts_ready"] is True
    assert payload["openai_tts_model"] == "gpt-4o-mini-tts"
    assert payload["openai_tts_voice"] == "cedar"
    assert "super-secret-test-key" not in str(payload)


def test_v4_speech_requires_openai_key(monkeypatch, tmp_path):
    monkeypatch.setenv("HAKHAM_MODEL_PROVIDER", "ollama")
    monkeypatch.setenv("HAKHAM_MODEL", "llama3.2")
    monkeypatch.setenv("HAKHAM_MEMORY_DB", str(tmp_path / "hakham.db"))
    monkeypatch.setenv("OPENAI_API_KEY", "")

    response = TestClient(app).post("/api/voice/speech", json={"text": "Shalom, Ach"})

    assert response.status_code == 503


def test_v4_speech_returns_mp3_without_exposing_key(monkeypatch, tmp_path):
    monkeypatch.setenv("HAKHAM_MODEL_PROVIDER", "ollama")
    monkeypatch.setenv("HAKHAM_MODEL", "llama3.2")
    monkeypatch.setenv("HAKHAM_MEMORY_DB", str(tmp_path / "hakham.db"))
    monkeypatch.setenv("OPENAI_API_KEY", "super-secret-test-key")
    monkeypatch.setattr(OpenAITTSClient, "synthesize", lambda self, text: b"fake-mp3")

    response = TestClient(app).post("/api/voice/speech", json={"text": "Shalom, Ach"})

    assert response.status_code == 200
    assert response.content == b"fake-mp3"
    assert response.headers["content-type"].startswith("audio/mpeg")
    assert response.headers["cache-control"] == "no-store"
