import pytest

from hakham.memory import MemoryKind, MemoryStore
from hakham.promotion import MemoryPromoter
from hakham.provenance import ProvenanceLedger
from hakham.quarantine import MemoryQuarantine


def build(tmp_path):
    path = tmp_path / "hakham.db"
    return (
        MemoryStore(str(path)),
        MemoryQuarantine(str(path)),
        ProvenanceLedger(str(path)),
    )


def test_pending_item_cannot_be_promoted(tmp_path):
    store, quarantine, provenance = build(tmp_path)
    item = quarantine.add(
        "Candidate domain is example.com",
        kind=MemoryKind.FACT.value,
        source="chatgpt-export",
        importance=70,
        subject_key="project domain",
        reason="historical claim",
    )
    promoter = MemoryPromoter(store, quarantine, provenance)
    with pytest.raises(ValueError):
        promoter.promote(item.id)


def test_approved_item_is_promoted_with_audit_trail(tmp_path):
    store, quarantine, provenance = build(tmp_path)
    item = quarantine.add(
        "The official domain is example.com",
        kind=MemoryKind.FACT.value,
        source="chatgpt-export",
        importance=80,
        subject_key="project domain",
        reason="historical claim",
    )
    quarantine.review(
        item.id,
        status="approved",
        note="validated against current project records",
        reviewed_by="user-explicit",
    )

    result = MemoryPromoter(store, quarantine, provenance).promote(item.id)
    assert result.memory.content == "The official domain is example.com"
    assert store.search("example.com")[0].id == result.memory.id

    events = provenance.history(result.memory.id)
    assert events[0].event_type == "promoted_from_quarantine"
    assert events[0].quarantine_id == item.id
    assert events[0].actor == "user-explicit"


def test_promotion_can_supersede_active_memory_and_preserve_chain(tmp_path):
    store, quarantine, provenance = build(tmp_path)
    old = store.remember(
        "The official domain is old.example",
        kind=MemoryKind.FACT,
        source="user-explicit",
        importance=90,
        subject_key="project domain",
    )
    item = quarantine.add(
        "The official domain is new.example",
        kind=MemoryKind.FACT.value,
        source="google-drive",
        importance=95,
        subject_key="project domain",
        reason="conflicting first-party record",
    )
    quarantine.review(
        item.id,
        status="approved",
        note="confirmed as current",
        reviewed_by="user-explicit",
    )

    result = MemoryPromoter(store, quarantine, provenance).promote(item.id)
    assert result.replaced_memory_id == old.id
    assert result.memory.supersedes_id == old.id

    old_history = provenance.history(old.id)
    assert old_history[0].event_type == "superseded_by_promotion"
    assert old_history[0].related_memory_id == result.memory.id
