import pytest
from fastapi.testclient import TestClient

from hakham import web as backend
from hakham.web_v5 import app


@pytest.fixture(autouse=True)
def reset_runtime_state():
    backend.runtime._runtime = None
    backend.runtime._fingerprint = None
    backend.runtime._mode = None
    yield
    backend.runtime._runtime = None
    backend.runtime._fingerprint = None
    backend.runtime._mode = None


def _base_env(monkeypatch, tmp_path):
    monkeypatch.setenv("HAKHAM_MODEL_PROVIDER", "ollama")
    monkeypatch.setenv("HAKHAM_MODEL", "llama3.2")
    monkeypatch.setenv("HAKHAM_MEMORY_DB", str(tmp_path / "hakham.db"))


def test_v5_home_exposes_premium_hud_agents_tools_and_voice_scope(monkeypatch, tmp_path):
    _base_env(monkeypatch, tmp_path)

    response = TestClient(app).get("/")

    assert response.status_code == 200
    assert "HAKHAM INFINITY ∞ v0.5" in response.text
    assert "EQUIPE DE AGENTES" in response.text
    assert "TOOL GATEWAY" in response.text
    assert "voiceScope" in response.text
    assert "HAKHAM · AVATAR OFICIAL" in response.text
    assert "/api/agents/delegate" in response.text


def test_v5_status_reports_agent_and_tool_counts_without_secrets(monkeypatch, tmp_path):
    _base_env(monkeypatch, tmp_path)
    monkeypatch.setenv("EVOLUTION_API_URL", "https://example.invalid")
    monkeypatch.setenv("EVOLUTION_API_KEY", "top-secret")
    monkeypatch.setenv("EVOLUTION_INSTANCE", "hakham")

    payload = TestClient(app).get("/api/status").json()

    assert payload["version"] == "0.5.0"
    assert payload["agent_count"] >= 6
    assert payload["tool_count"] >= 5
    assert payload["tool_configured_count"] >= 2
    assert "top-secret" not in str(payload)


def test_v5_agents_endpoint_lists_specialists(monkeypatch, tmp_path):
    _base_env(monkeypatch, tmp_path)
    payload = TestClient(app).get("/api/agents").json()
    ids = {item["id"] for item in payload["items"]}

    assert {"hakham", "serafim", "arcanum", "delta", "luna", "ser-master"}.issubset(ids)


def test_v5_tool_gateway_blocks_sensitive_action_without_approval(monkeypatch, tmp_path):
    _base_env(monkeypatch, tmp_path)
    monkeypatch.setenv("EVOLUTION_API_URL", "https://example.invalid")
    monkeypatch.setenv("EVOLUTION_API_KEY", "key")
    monkeypatch.setenv("EVOLUTION_INSTANCE", "hakham")

    response = TestClient(app).post(
        "/api/tools/execute",
        json={
            "tool_id": "whatsapp.send_text",
            "arguments": {"number": "5585999999999", "text": "Shalom"},
            "approved": False,
        },
    )

    assert response.status_code == 403
