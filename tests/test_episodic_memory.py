from hakham.episodic import EpisodicStore
from hakham.memory import MemoryKind, MemoryStore


def test_episodic_store_preserves_order_and_session(tmp_path):
    path = tmp_path / "hakham.db"
    store = EpisodicStore(str(path))
    store.append("user", "primeira", session_id="a")
    store.append("assistant", "segunda", session_id="a")
    store.append("user", "outra sessao", session_id="b")

    recent = store.recent(10, session_id="a")
    assert [item.content for item in recent] == ["segunda", "primeira"]
    assert all(item.session_id == "a" for item in recent)


def test_semantic_recent_is_chronological_not_importance_ranked(tmp_path):
    path = tmp_path / "hakham.db"
    store = MemoryStore(str(path))
    first = store.remember("important old", kind=MemoryKind.FACT, importance=100)
    second = store.remember("new low importance", kind=MemoryKind.FACT, importance=1)

    recent = store.recent(2)
    important = store.important(2)

    assert recent[0].id == second.id
    assert important[0].id == first.id
