from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass

from .embeddings import EmbeddingProvider, cosine_similarity
from .memory import Memory, MemoryStore


STOPWORDS = {
    "a", "o", "as", "os", "de", "da", "do", "das", "dos", "e", "em", "no", "na",
    "nos", "nas", "um", "uma", "para", "por", "com", "que", "qual", "quais", "como",
    "the", "a", "an", "of", "to", "and", "in", "on", "for", "with", "what", "which",
}


@dataclass(frozen=True)
class RetrievedMemory:
    memory: Memory
    score: float
    lexical_score: float = 0.0
    vector_score: float = 0.0


class MemoryRetriever:
    """Hybrid relevance ranking with a dependency-light local fallback.

    Lexical relevance is always available. When an EmbeddingProvider is
    supplied, vector similarity is blended into the final score. This keeps
    HAKHAM functional offline and prevents vendor lock-in.
    """

    def __init__(self, store: MemoryStore, embedder: EmbeddingProvider | None = None) -> None:
        self.store = store
        self.embedder = embedder

    @staticmethod
    def _normalize(text: str) -> str:
        text = unicodedata.normalize("NFKD", text.casefold())
        text = "".join(ch for ch in text if not unicodedata.combining(ch))
        return re.sub(r"[^a-z0-9]+", " ", text).strip()

    @classmethod
    def _tokens(cls, text: str) -> list[str]:
        return [token for token in cls._normalize(text).split() if len(token) > 1 and token not in STOPWORDS]

    @staticmethod
    def _cosine(left: Counter[str], right: Counter[str]) -> float:
        if not left or not right:
            return 0.0
        dot = sum(value * right.get(token, 0) for token, value in left.items())
        left_norm = math.sqrt(sum(value * value for value in left.values()))
        right_norm = math.sqrt(sum(value * value for value in right.values()))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return dot / (left_norm * right_norm)

    def relevant(self, query: str, *, limit: int = 6, candidate_limit: int = 200) -> list[RetrievedMemory]:
        query_tokens = self._tokens(query)
        if not query_tokens:
            return [RetrievedMemory(memory=item, score=item.importance / 100) for item in self.store.recent(limit)]

        query_counter = Counter(query_tokens)
        query_vector = self.embedder.embed(query) if self.embedder else None
        candidates = self.store.recent(candidate_limit)
        ranked: list[RetrievedMemory] = []

        for memory in candidates:
            text = f"{memory.subject_key or ''} {memory.content}"
            memory_counter = Counter(self._tokens(text))
            semantic = self._cosine(query_counter, memory_counter)
            overlap = len(set(query_tokens) & set(memory_counter)) / max(1, len(set(query_tokens)))
            lexical = (semantic * 0.68) + (overlap * 0.32)
            vector = 0.0
            if self.embedder and query_vector is not None:
                memory_vector = self.embedder.embed(text)
                vector = max(0.0, cosine_similarity(query_vector, memory_vector))

            importance = memory.importance / 100
            if self.embedder:
                score = (lexical * 0.45) + (vector * 0.40) + (importance * 0.15)
            else:
                score = (lexical * 0.80) + (importance * 0.20)

            if lexical > 0 or vector > 0:
                ranked.append(
                    RetrievedMemory(
                        memory=memory,
                        score=round(score, 4),
                        lexical_score=round(lexical, 4),
                        vector_score=round(vector, 4),
                    )
                )

        ranked.sort(key=lambda item: (item.score, item.memory.id), reverse=True)
        return ranked[:limit]
