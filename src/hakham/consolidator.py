from __future__ import annotations

import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass

from .episodic import EpisodicStore
from .memory import MemoryKind
from .memory_extractor import MemoryCandidate, MemoryExtractor


@dataclass(frozen=True)
class ConsolidationCandidate:
    content: str
    kind: str
    importance: int
    source: str
    evidence_count: int
    episode_ids: tuple[int, ...]


class MemoryConsolidator:
    """Detect repeated semantic candidates in episodic user conversation.

    This stage never promotes directly to durable memory. It only emits
    candidates with evidence references. Policy decisions happen downstream.
    """

    def __init__(self, episodic: EpisodicStore, extractor: MemoryExtractor | None = None) -> None:
        self.episodic = episodic
        self.extractor = extractor or MemoryExtractor()

    @staticmethod
    def _normalize(text: str) -> str:
        text = unicodedata.normalize("NFKD", text.casefold())
        text = "".join(ch for ch in text if not unicodedata.combining(ch))
        text = re.sub(r"[^a-z0-9]+", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    @classmethod
    def _signature(cls, content: str, kind: MemoryKind | str) -> str:
        kind_value = kind.value if isinstance(kind, MemoryKind) else str(kind)
        return f"{kind_value}:{cls._normalize(content)}"

    def candidates(
        self,
        *,
        session_id: str = "default",
        episode_limit: int = 200,
        min_evidence: int = 2,
    ) -> list[ConsolidationCandidate]:
        episodes = list(reversed(self.episodic.recent(episode_limit, session_id=session_id)))
        buckets: dict[str, list[tuple[int, MemoryCandidate]]] = defaultdict(list)

        for episode in episodes:
            if episode.role != "user":
                continue
            extracted = self.extractor.extract(episode.content, source="episodic-consolidation")
            for candidate in extracted:
                kind_value = candidate.kind.value
                if kind_value == MemoryKind.CONVERSATION.value:
                    continue
                signature = self._signature(candidate.content, candidate.kind)
                buckets[signature].append((episode.id, candidate))

        results: list[ConsolidationCandidate] = []
        for grouped in buckets.values():
            if len(grouped) < min_evidence:
                continue
            episode_ids = tuple(item[0] for item in grouped)
            exemplar = grouped[-1][1]
            importance = min(100, exemplar.importance + min(15, (len(grouped) - 1) * 5))
            results.append(
                ConsolidationCandidate(
                    content=exemplar.content,
                    kind=exemplar.kind.value,
                    importance=importance,
                    source="episodic-consolidation",
                    evidence_count=len(grouped),
                    episode_ids=episode_ids,
                )
            )

        results.sort(key=lambda item: (item.evidence_count, item.importance), reverse=True)
        return results
