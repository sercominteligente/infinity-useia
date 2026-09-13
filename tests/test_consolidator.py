from hakham.consolidator import MemoryConsolidator
from hakham.episodic import EpisodicStore
from hakham.memory import MemoryStore
from hakham.memory_guard import MemoryGuard
from hakham.quarantine import MemoryQuarantine


def test_repeated_user_pattern_becomes_consolidation_candidate(tmp_path):
    db = tmp_path / "hakham.db"
    episodic = EpisodicStore(str(db))
    episodic.append("user", "O projeto Portal Luna usa foco educacional")
    episodic.append("assistant", "Entendido")
    episodic.append("user", "O projeto Portal Luna usa foco educacional")

    candidates = MemoryConsolidator(episodic).candidates(min_evidence=2)

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.kind == "project"
    assert candidate.evidence_count == 2
    assert len(candidate.episode_ids) == 2
    assert candidate.source == "episodic-consolidation"


def test_single_mention_does_not_consolidate(tmp_path):
    db = tmp_path / "hakham.db"
    episodic = EpisodicStore(str(db))
    episodic.append("user", "O projeto Portal Luna usa foco educacional")

    candidates = MemoryConsolidator(episodic).candidates(min_evidence=2)

    assert candidates == []


def test_consolidated_pattern_is_quarantined_not_activated(tmp_path):
    db = tmp_path / "hakham.db"
    episodic = EpisodicStore(str(db))
    store = MemoryStore(str(db))
    quarantine = MemoryQuarantine(str(db))
    guard = MemoryGuard(store, quarantine)

    episodic.append("user", "O projeto Portal Luna usa foco educacional")
    episodic.append("user", "O projeto Portal Luna usa foco educacional")
    candidate = MemoryConsolidator(episodic).candidates(min_evidence=2)[0]

    result = guard.ingest(
        candidate.content,
        kind=candidate.kind,
        source=candidate.source,
        importance=candidate.importance,
    )

    assert result.action == "quarantine"
    assert result.quarantine is not None
    assert store.search("Portal Luna") == []
    assert len(quarantine.pending()) == 1
