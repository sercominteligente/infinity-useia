from hakham.memory import MemoryKind, MemoryStatus, MemoryStore


def test_exact_duplicate_returns_existing_memory(tmp_path):
    store = MemoryStore(str(tmp_path / "hakham.db"))
    first = store.remember("SERhub is an ERP", kind=MemoryKind.FACT)
    second = store.remember("SERhub is an ERP", kind=MemoryKind.FACT)

    assert first.id == second.id
    assert len(store.search("SERhub", include_superseded=True)) == 1


def test_new_decision_can_supersede_previous_one(tmp_path):
    store = MemoryStore(str(tmp_path / "hakham.db"))
    old = store.remember(
        "NegocIAJa will launch as a broad marketplace",
        kind=MemoryKind.DECISION,
        subject_key="negociaja launch strategy",
        importance=90,
    )
    new = store.remember(
        "NegocIAJa will launch as a focused lead-generation pilot",
        kind=MemoryKind.DECISION,
        subject_key="negociaja launch strategy",
        importance=95,
        supersede_existing=True,
    )

    active = store.history("negociaja launch strategy", MemoryKind.DECISION)
    assert active[0].id == new.id
    assert active[0].status == MemoryStatus.ACTIVE.value
    assert active[0].supersedes_id == old.id
    assert active[1].status == MemoryStatus.SUPERSEDED.value


def test_superseded_memories_are_hidden_from_normal_retrieval(tmp_path):
    store = MemoryStore(str(tmp_path / "hakham.db"))
    store.remember(
        "Old domain is example-old.test",
        kind=MemoryKind.FACT,
        subject_key="official domain",
    )
    store.remember(
        "Current domain is example-new.test",
        kind=MemoryKind.FACT,
        subject_key="official domain",
        supersede_existing=True,
    )

    visible = store.recent(10)
    assert len(visible) == 1
    assert "example-new.test" in visible[0].content

    full = store.recent(10, include_superseded=True)
    assert len(full) == 2
