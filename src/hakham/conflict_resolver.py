from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .memory import Memory


DEFAULT_SOURCE_TRUST = {
    "user-explicit": 100,
    "conversation": 85,
    "github": 90,
    "google-drive": 88,
    "chatgpt-export": 65,
    "agent": 60,
    "web": 55,
}


@dataclass(frozen=True)
class ConflictDecision:
    action: str
    winner: str
    existing_score: float
    candidate_score: float
    reason: str


class MemoryConflictResolver:
    """Rank conflicting memories without silently declaring truth.

    The resolver can recommend keeping, replacing or reviewing. It never
    mutates the MemoryStore itself.
    """

    def __init__(self, source_trust: dict[str, int] | None = None) -> None:
        self.source_trust = {**DEFAULT_SOURCE_TRUST, **(source_trust or {})}

    def _source_score(self, source: str) -> int:
        if source.startswith("agent:"):
            return self.source_trust.get("agent", 60)
        return self.source_trust.get(source, 50)

    @staticmethod
    def _recency_score(created_at: str) -> float:
        try:
            created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
        except ValueError:
            return 0.0
        age_days = max(0.0, (datetime.now(timezone.utc) - created).total_seconds() / 86400)
        return max(0.0, 100.0 - min(age_days, 3650.0) / 36.5)

    def score(self, memory: Memory) -> float:
        source = self._source_score(memory.source)
        importance = memory.importance
        recency = self._recency_score(memory.created_at)
        return round((source * 0.50) + (importance * 0.30) + (recency * 0.20), 2)

    def resolve(self, existing: Memory, candidate: Memory) -> ConflictDecision:
        existing_score = self.score(existing)
        candidate_score = self.score(candidate)

        if existing.content.strip().casefold() == candidate.content.strip().casefold():
            return ConflictDecision(
                action="deduplicate",
                winner="existing",
                existing_score=existing_score,
                candidate_score=candidate_score,
                reason="same normalized content",
            )

        delta = candidate_score - existing_score
        if delta >= 15:
            return ConflictDecision(
                action="replace",
                winner="candidate",
                existing_score=existing_score,
                candidate_score=candidate_score,
                reason="candidate has materially stronger authority/confidence score",
            )
        if delta <= -15:
            return ConflictDecision(
                action="keep",
                winner="existing",
                existing_score=existing_score,
                candidate_score=candidate_score,
                reason="existing memory has materially stronger authority/confidence score",
            )
        return ConflictDecision(
            action="review",
            winner="none",
            existing_score=existing_score,
            candidate_score=candidate_score,
            reason="scores are too close for automatic replacement",
        )
