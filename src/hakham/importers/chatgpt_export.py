from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ..memory_extractor import MemoryCandidate, MemoryExtractor


@dataclass(frozen=True)
class ImportedTurn:
    conversation_id: str
    role: str
    text: str
    source: str = "chatgpt-export"


class ChatGPTExportImporter:
    """Safe staging layer for historical ChatGPT exports.

    The real export parser will be adapted to the exact schema received from
    OpenAI. Until then, this class only accepts normalized turns. Historical
    content is treated as evidence, never as automatically current truth.
    """

    def __init__(self, extractor: MemoryExtractor | None = None) -> None:
        self.extractor = extractor or MemoryExtractor()

    def extract_candidates(self, turns: Iterable[ImportedTurn]) -> list[MemoryCandidate]:
        candidates: list[MemoryCandidate] = []
        for turn in turns:
            if turn.role != "user":
                continue
            candidates.extend(self.extractor.extract(turn.text, source=turn.source))
        return candidates
