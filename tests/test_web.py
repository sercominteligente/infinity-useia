from fastapi.testclient import TestClient

from hakham.memory import MemoryStore
from hakham.web import app


def test_control_center_home_and_status(monkeypatch, tmp_path):
    db = tmp_path / "hakham.db"
    monkeypatch.setenv("HAKHAM_MODEL_PROVIDER", "ollama")
    monkeypatch.setenv("HAKHAM_MODEL", "llama3.2")
    monkeypatch.setenv("HAKHAM_MEMORY_DB", str(db))

    client = TestClient(app)

    home = client.get("/")
    assert home.status_code == 200
    assert "HAKHAM CONTROL CENTER" in home.text
    assert "onde vamos" in home.text
    assert "ASTRA" in home.text
    assert "CONSELHO" in home.text

    status = client.get("/api/status")
    assert status.status_code == 200
    payload = status.json()
    assert payload["name"] == "HAKHAM Infinity"
    assert payload["version"] == "0.2.0"
    assert payload["provider"] == "ollama"
    assert payload["model"] == "llama3.2"


def test_recent_search_projects_and_tasks(monkeypatch, tmp_path):
    db = tmp_path / "hakham.db"
    monkeypatch.setenv("HAKHAM_MEMORY_DB", str(db))
    store = MemoryStore(str(db))
    store.remember("Portal Luna e um projeto educacional", kind="project")
    store.remember("Preparar o proximo sprint", kind="task")

    client = TestClient(app)

    recent = client.get("/api/memory/recent?limit=5")
    assert recent.status_code == 200
    assert len(recent.json()["items"]) == 2

    search = client.get("/api/memory/search?q=Luna")
    assert search.status_code == 200
    assert search.json()["items"][0]["content"] == "Portal Luna e um projeto educacional"

    projects = client.get("/api/projects")
    assert projects.status_code == 200
    assert projects.json()["items"][0]["kind"] == "project"

    tasks = client.get("/api/tasks")
    assert tasks.status_code == 200
    assert tasks.json()["items"][0]["kind"] == "task"


def test_manual_memory_is_user_explicit(monkeypatch, tmp_path):
    db = tmp_path / "hakham.db"
    monkeypatch.setenv("HAKHAM_MEMORY_DB", str(db))
    client = TestClient(app)

    response = client.post(
        "/api/memory",
        json={"content": "HAKHAM usa memoria propria", "kind": "fact", "importance": 90},
    )
    assert response.status_code == 200
    item = response.json()["item"]
    assert item["source"] == "user-explicit"
    assert item["importance"] == 90


def test_models_endpoint_requires_abacus_key(monkeypatch, tmp_path):
    monkeypatch.setenv("HAKHAM_MODEL_PROVIDER", "abacus")
    monkeypatch.setenv("HAKHAM_MODEL", "route-llm")
    monkeypatch.setenv("HAKHAM_MEMORY_DB", str(tmp_path / "hakham.db"))
    monkeypatch.delenv("ABACUS_ROUTELLM_API_KEY", raising=False)

    client = TestClient(app)
    response = client.get("/api/models")
    assert response.status_code == 503
    assert "Abacus key" in response.json()["detail"]


def test_dashboard_can_switch_between_astra_and_auto_without_network(monkeypatch, tmp_path):
    monkeypatch.setenv("HAKHAM_MODEL_PROVIDER", "abacus")
    monkeypatch.setenv("HAKHAM_MODEL", "route-llm")
    monkeypatch.setenv("HAKHAM_MEMORY_DB", str(tmp_path / "hakham.db"))
    monkeypatch.setenv("ABACUS_ROUTELLM_API_KEY", "test-key")
    monkeypatch.delenv("HAKHAM_COUNCIL_MODELS", raising=False)

    client = TestClient(app)

    astra = client.post("/api/mode", json={"mode": "astra"})
    assert astra.status_code == 200
    assert astra.json()["mode"] == "astra"
    assert astra.json()["model"] == "gpt-6-astra"

    auto = client.post("/api/mode", json={"mode": "auto"})
    assert auto.status_code == 200
    assert auto.json()["mode"] == "auto"
    assert auto.json()["model"] == "route-llm"

    council = client.post("/api/mode", json={"mode": "council"})
    assert council.status_code == 400
    assert "HAKHAM_COUNCIL_MODELS" in council.json()["detail"]
