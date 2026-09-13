from __future__ import annotations

import re
from dataclasses import dataclass

from .memory import MemoryKind


@dataclass(frozen=True)
class MemoryCandidate:
    content: str
    kind: MemoryKind
    importance: int
    source: str = "conversation"


class MemoryExtractor:
    """First-pass deterministic memory extractor.

    This stage intentionally avoids an LLM dependency. It detects strong,
    explicit signals and promotes only high-confidence items. A later semantic
    extractor may enrich this output, but it must not silently override source
    provenance or high-confidence user decisions.
    """

    _PROJECT = re.compile(r"\b(projeto|project|portal|plataforma|sistema|produto)\b", re.I)
    _DECISION = re.compile(r"\b(decidimos|decisão|fica definido|vamos usar|será|foi aprovado|aprovado)\b", re.I)
    _PREFERENCE = re.compile(r"\b(prefiro|gosto|não quero|quero manter|sempre use|nunca use)\b", re.I)
    _TASK = re.compile(r"\b(precisamos|temos que|faça|crie|corrija|implemente|próximo passo)\b", re.I)
    _FACT = re.compile(r"\b(é|são|tem|possui|usa|utiliza|fica em|domínio|repo|repositório)\b", re.I)

    def extract(self, text: str, *, source: str = "conversation") -> list[MemoryCandidate]:
        text = " ".join(text.split()).strip()
        if not text:
            return []

        candidates: list[MemoryCandidate] = []
        if self._DECISION.search(text):
            candidates.append(MemoryCandidate(text, MemoryKind.DECISION, 90, source))
        elif self._PREFERENCE.search(text):
            candidates.append(MemoryCandidate(text, MemoryKind.PREFERENCE, 80, source))
        elif self._TASK.search(text):
            candidates.append(MemoryCandidate(text, MemoryKind.TASK, 75, source))
        elif self._PROJECT.search(text):
            candidates.append(MemoryCandidate(text, MemoryKind.PROJECT, 80, source))
        elif self._FACT.search(text):
            candidates.append(MemoryCandidate(text, MemoryKind.FACT, 65, source))

        return candidates
