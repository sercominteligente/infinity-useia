from __future__ import annotations

from dataclasses import dataclass

from .memory import Memory, MemoryStore
from .provenance import ProvenanceLedger
from .quarantine import MemoryQuarantine


@dataclass(frozen=True)
class PromotionResult:
    memory: Memory
    replaced_memory_id: int | None
    quarantine_id: int


class MemoryPromoter:
    """Promote explicitly approved quarantine items into active memory.

    Promotion is only allowed after review status becomes `approved`.
    Provenance is appended for both the promotion and any supersession.
    """

    def __init__(
        self,
        store: MemoryStore,
        quarantine: MemoryQuarantine,
        provenance: ProvenanceLedger,
    ) -> None:
        self.store = store
        self.quarantine = quarantine
        self.provenance = provenance

    def promote(self, item_id: int) -> PromotionResult:
        item = self.quarantine.get(item_id)
        if item.status != "approved":
            raise ValueError("only approved quarantine items can be promoted")

        existing = None
        if item.subject_key:
            existing = next(
                (
                    memory
                    for memory in self.store.history(item.subject_key, item.kind)
                    if memory.status == "active"
                ),
                None,
            )

        memory = self.store.remember(
            item.content,
            kind=item.kind,
            source=item.source,
            importance=item.importance,
            subject_key=item.subject_key,
            supersede_existing=existing is not None,
        )

        actor = item.reviewed_by or "reviewer:unknown"
        details = item.review_note or item.reason

        self.provenance.record(
            memory.id,
            event_type="promoted_from_quarantine",
            source=item.source,
            actor=actor,
            details=details,
            related_memory_id=existing.id if existing is not None else None,
            quarantine_id=item.id,
        )

        if existing is not None and memory.id != existing.id:
            self.provenance.record(
                existing.id,
                event_type="superseded_by_promotion",
                source=item.source,
                actor=actor,
                details=details,
                related_memory_id=memory.id,
                quarantine_id=item.id,
            )

        return PromotionResult(
            memory=memory,
            replaced_memory_id=existing.id if existing is not None else None,
            quarantine_id=item.id,
        )
