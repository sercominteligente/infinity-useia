from hakham.memory import MemoryKind, MemoryStore
from hakham.memory_guard import MemoryGuard
from hakham.quarantine import MemoryQuarantine


def build_guard(tmp_path):
    path = tmp_path / "hakham.db"
    return MemoryGuard(MemoryStore(str(path)), MemoryQuarantine(str(path)))


def test_historical_export_subject_is_quarantined(tmp_path):
    guard = build_guard(tmp_path)
    result = guard.ingest(
        "The project domain is old.example",
        kind=MemoryKind.FACT,
        source="chatgpt-export",
        importance=70,
        subject_key="project domain",
    )
    assert result.action == "quarantine"
    assert result.quarantine is not None
    assert guard.store.search("old.example") == []


def test_first_explicit_user_memory_is_active(tmp_path):
    guard = build_guard(tmp_path)
    result = guard.ingest(
        "The official domain is new.example",
        kind=MemoryKind.FACT,
        source="user-explicit",
        importance=95,
        subject_key="project domain",
    )
    assert result.action == "stored"
    assert result.memory is not None
    assert result.memory.status == "active"


def test_review_queue_is_auditable(tmp_path):
    guard = build_guard(tmp_path)
    result = guard.ingest(
        "Historical candidate",
        kind=MemoryKind.DECISION,
        source="chatgpt-export",
        importance=60,
        subject_key="launch strategy",
    )
    item = result.quarantine
    reviewed = guard.quarantine.review(item.id, status="rejected", note="superseded by current decision")
    assert reviewed.status == "rejected"
    assert reviewed.review_note == "superseded by current decision"
    assert guard.quarantine.pending() == []
