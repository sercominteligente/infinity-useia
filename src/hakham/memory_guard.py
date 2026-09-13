from __future__ import annotations

from dataclasses import dataclass

from .conflict_resolver import MemoryConflictResolver
from .memory import Memory, MemoryKind, MemoryStore
from .quarantine import MemoryQuarantine, QuarantinedMemory


@dataclass(frozen=True)
class GuardResult:
    action: str
    memory: Memory | None = None
    quarantine: QuarantinedMemory | None = None
    reason: str = ""


class MemoryGuard:
    """Policy gate between candidate memories and the active memory store."""

    def __init__(
        self,
        store: MemoryStore,
        quarantine: MemoryQuarantine,
        resolver: MemoryConflictResolver | None = None,
    ) -> None:
        self.store = store
        self.quarantine = quarantine
        self.resolver = resolver or MemoryConflictResolver()

    def ingest(
        self,
        content: str,
        *,
        kind: MemoryKind | str,
        source: str,
        importance: int,
        subject_key: str | None = None,
    ) -> GuardResult:
        kind_value = kind.value if isinstance(kind, MemoryKind) else str(kind)

        # Learned patterns from repeated conversation are hypotheses, not truth.
        # They always require review before promotion to semantic memory.
        if source == "episodic-consolidation":
            item = self.quarantine.add(
                content,
                kind=kind_value,
                source=source,
                importance=importance,
                subject_key=subject_key,
                reason="learned episodic pattern requires review before becoming durable memory",
            )
            return GuardResult("quarantine", quarantine=item, reason=item.reason)

        # Historical imports and open-web claims are evidence, not automatic truth
        # when they target a mutable subject.
        if subject_key and source in {"chatgpt-export", "web"}:
            item = self.quarantine.add(
                content,
                kind=kind_value,
                source=source,
                importance=importance,
                subject_key=subject_key,
                reason="historical/external claim requires validation before becoming active",
            )
            return GuardResult("quarantine", quarantine=item, reason=item.reason)

        history = self.store.history(subject_key, kind_value) if subject_key else []
        existing = next((item for item in history if item.status == "active"), None)
        if existing is None:
            memory = self.store.remember(
                content,
                kind=kind_value,
                source=source,
                importance=importance,
                subject_key=subject_key,
            )
            return GuardResult("stored", memory=memory, reason="no active conflict")

        candidate = Memory(
            id=-1,
            content=content.strip(),
            created_at=existing.created_at,
            kind=kind_value,
            source=source,
            importance=importance,
            subject_key=subject_key,
        )
        decision = self.resolver.resolve(existing, candidate)

        if decision.action == "deduplicate":
            return GuardResult("deduplicated", memory=existing, reason=decision.reason)

        if decision.action == "replace":
            memory = self.store.remember(
                content,
                kind=kind_value,
                source=source,
                importance=importance,
                subject_key=subject_key,
                supersede_existing=True,
            )
            return GuardResult("replaced", memory=memory, reason=decision.reason)

        item = self.quarantine.add(
            content,
            kind=kind_value,
            source=source,
            importance=importance,
            subject_key=subject_key,
            reason=f"conflict resolver: {decision.action}; {decision.reason}",
        )
        return GuardResult("quarantine", memory=existing, quarantine=item, reason=item.reason)
