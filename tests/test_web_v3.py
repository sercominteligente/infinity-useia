import pytest
from fastapi.testclient import TestClient

from hakham import web as backend
from hakham.web_v3 import app


@pytest.fixture(autouse=True)
def reset_runtime_state():
    backend.runtime._runtime = None
    backend.runtime._fingerprint = None
    backend.runtime._mode = None
    yield
    backend.runtime._runtime = None
    backend.runtime._fingerprint = None
    backend.runtime._mode = None


def test_v3_home_exposes_voice_loop_and_interactive_states(monkeypatch, tmp_path):
    monkeypatch.setenv("HAKHAM_MODEL_PROVIDER", "ollama")
    monkeypatch.setenv("HAKHAM_MODEL", "llama3.2")
    monkeypatch.setenv("HAKHAM_MEMORY_DB", str(tmp_path / "hakham.db"))

    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert "HAKHAM CONTROL CENTER" in response.text
    assert "ATIVAR MICROFONE" in response.text
    assert "RESPOSTA POR VOZ" in response.text
    assert "OUVINDO O ACH" in response.text
    assert "HAKHAM PENSANDO" in response.text
    assert "HAKHAM FALANDO" in response.text
    assert "SpeechRecognition" in response.text
    assert "SpeechSynthesisUtterance" in response.text


def test_v3_status_reports_version_and_runtime(monkeypatch, tmp_path):
    monkeypatch.setenv("HAKHAM_MODEL_PROVIDER", "ollama")
    monkeypatch.setenv("HAKHAM_MODEL", "llama3.2")
    monkeypatch.setenv("HAKHAM_MEMORY_DB", str(tmp_path / "hakham.db"))

    client = TestClient(app)
    response = client.get("/api/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["version"] == "0.3.0"
    assert payload["provider"] == "ollama"
    assert payload["model"] == "llama3.2"


def test_v3_can_switch_abacus_runtime_between_astra_and_auto(monkeypatch, tmp_path):
    monkeypatch.setenv("HAKHAM_MODEL_PROVIDER", "abacus")
    monkeypatch.setenv("HAKHAM_MODEL", "gpt-6-astra")
    monkeypatch.setenv("ABACUS_ROUTELLM_API_KEY", "test-key")
    monkeypatch.setenv("HAKHAM_MEMORY_DB", str(tmp_path / "hakham.db"))

    client = TestClient(app)

    astra = client.post("/api/mode", json={"mode": "astra"})
    assert astra.status_code == 200
    assert astra.json()["model"] == "gpt-6-astra"
    assert astra.json()["mode"] == "astra"

    auto = client.post("/api/mode", json={"mode": "auto"})
    assert auto.status_code == 200
    assert auto.json()["model"] == "route-llm"
    assert auto.json()["mode"] == "auto"
