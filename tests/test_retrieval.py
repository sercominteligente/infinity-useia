from hakham.memory import MemoryKind, MemoryStore
from hakham.retrieval import MemoryRetriever


def test_retrieval_finds_related_project_memory(tmp_path):
    store = MemoryStore(str(tmp_path / "hakham.db"))
    store.remember(
        "O NegocIAJá será lançado como piloto focado em geração de leads para pequenos negócios de Maracanaú.",
        kind=MemoryKind.DECISION,
        source="user-explicit",
        importance=95,
        subject_key="negociaja launch strategy",
    )
    store.remember(
        "O Portal Luna terá professores seniores por área do conhecimento.",
        kind=MemoryKind.PROJECT,
        source="user-explicit",
        importance=90,
        subject_key="portal luna teachers",
    )

    results = MemoryRetriever(store).relevant(
        "Qual foi a estratégia de lançamento do NegocIAJá em Maracanaú?",
        limit=2,
    )

    assert results
    assert "NegocIAJá" in results[0].memory.content


def test_retrieval_ignores_unrelated_memories(tmp_path):
    store = MemoryStore(str(tmp_path / "hakham.db"))
    store.remember(
        "O Portal Luna usa professores por disciplina.",
        kind=MemoryKind.PROJECT,
        source="user-explicit",
        importance=90,
    )

    results = MemoryRetriever(store).relevant("estratégia comercial do NegocIAJá")
    assert results == []


def test_retrieval_normalizes_accents(tmp_path):
    store = MemoryStore(str(tmp_path / "hakham.db"))
    store.remember(
        "A comunicacao visual terá uma vertical independente.",
        kind=MemoryKind.DECISION,
        source="user-explicit",
        importance=85,
    )

    results = MemoryRetriever(store).relevant("comunicação visual")
    assert len(results) == 1
