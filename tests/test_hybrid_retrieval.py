from hakham.embeddings import EmbeddingProvider, HashEmbeddingProvider, cosine_similarity
from hakham.memory import MemoryKind, MemoryStore
from hakham.retrieval import MemoryRetriever


class TopicEmbedder(EmbeddingProvider):
    def embed(self, text: str) -> list[float]:
        text = text.casefold()
        if "dominio" in text or "domain" in text or "site" in text:
            return [1.0, 0.0, 0.0]
        if "pagamento" in text or "payment" in text:
            return [0.0, 1.0, 0.0]
        return [0.0, 0.0, 1.0]


def test_hash_embeddings_are_deterministic():
    provider = HashEmbeddingProvider(dimensions=64)
    assert provider.embed("Portal Luna") == provider.embed("Portal Luna")


def test_cosine_rejects_dimension_mismatch():
    try:
        cosine_similarity([1.0], [1.0, 0.0])
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_vector_signal_can_retrieve_concept_with_different_words(tmp_path):
    store = MemoryStore(str(tmp_path / "memory.db"))
    store.remember(
        "O endereco oficial do projeto foi definido.",
        kind=MemoryKind.FACT,
        importance=85,
        subject_key="project domain",
    )
    store.remember(
        "Mercado Pago processa o checkout.",
        kind=MemoryKind.FACT,
        importance=85,
        subject_key="payments",
    )

    retriever = MemoryRetriever(store, embedder=TopicEmbedder())
    results = retriever.relevant("Qual é o site oficial?", limit=1)

    assert len(results) == 1
    assert results[0].memory.subject_key == "project domain"
    assert results[0].vector_score > 0


def test_retriever_still_works_without_embeddings(tmp_path):
    store = MemoryStore(str(tmp_path / "memory.db"))
    store.remember("Portal Luna usa professores de IA", kind=MemoryKind.PROJECT, importance=80)
    retriever = MemoryRetriever(store)
    results = retriever.relevant("professores Portal Luna")
    assert results
    assert results[0].memory.kind == MemoryKind.PROJECT.value
