import sqlite3

import pytest

from hakham.memory import MemoryKind, MemoryStore


def test_structured_memory_can_filter_by_kind(tmp_path):
    path = tmp_path / "hakham.db"
    store = MemoryStore(str(path))
    store.remember("Portal Luna is an education project", kind=MemoryKind.PROJECT, importance=90)
    store.remember("Use local models when possible", kind=MemoryKind.PREFERENCE, importance=70)

    projects = store.recent(kind=MemoryKind.PROJECT)
    assert len(projects) == 1
    assert projects[0].kind == "project"
    assert projects[0].importance == 90


def test_memory_keeps_provenance(tmp_path):
    store = MemoryStore(str(tmp_path / "hakham.db"))
    memory = store.remember(
        "Imported historical conversation",
        kind=MemoryKind.FACT,
        source="chatgpt-export",
        importance=80,
    )
    assert memory.source == "chatgpt-export"


def test_importance_is_bounded(tmp_path):
    store = MemoryStore(str(tmp_path / "hakham.db"))
    with pytest.raises(ValueError):
        store.remember("invalid", importance=101)


def test_old_database_is_migrated_without_losing_content(tmp_path):
    path = tmp_path / "legacy.db"
    with sqlite3.connect(path) as db:
        db.execute(
            "CREATE TABLE memories (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT NOT NULL, created_at TEXT NOT NULL)"
        )
        db.execute(
            "INSERT INTO memories(content, created_at) VALUES (?, ?)",
            ("legacy memory", "2026-01-01T00:00:00+00:00"),
        )

    store = MemoryStore(str(path))
    memories = store.search("legacy")
    assert memories[0].content == "legacy memory"
    assert memories[0].kind == "conversation"
