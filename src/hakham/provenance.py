from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class ProvenanceEvent:
    id: int
    memory_id: int
    event_type: str
    source: str
    actor: str | None
    details: str | None
    created_at: str
    related_memory_id: int | None = None
    quarantine_id: int | None = None


class ProvenanceLedger:
    """Append-only audit trail for memory state transitions."""

    def __init__(self, path: str = "data/hakham.db") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as db:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_provenance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    memory_id INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    source TEXT NOT NULL,
                    actor TEXT,
                    details TEXT,
                    created_at TEXT NOT NULL,
                    related_memory_id INTEGER,
                    quarantine_id INTEGER
                )
                """
            )
            db.execute(
                "CREATE INDEX IF NOT EXISTS idx_memory_provenance_memory ON memory_provenance(memory_id, id)"
            )

    @staticmethod
    def _from_row(row: sqlite3.Row) -> ProvenanceEvent:
        return ProvenanceEvent(
            id=int(row["id"]),
            memory_id=int(row["memory_id"]),
            event_type=row["event_type"],
            source=row["source"],
            actor=row["actor"],
            details=row["details"],
            created_at=row["created_at"],
            related_memory_id=row["related_memory_id"],
            quarantine_id=row["quarantine_id"],
        )

    def record(
        self,
        memory_id: int,
        *,
        event_type: str,
        source: str,
        actor: str | None = None,
        details: str | None = None,
        related_memory_id: int | None = None,
        quarantine_id: int | None = None,
    ) -> ProvenanceEvent:
        created_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as db:
            cursor = db.execute(
                """INSERT INTO memory_provenance(
                       memory_id, event_type, source, actor, details,
                       created_at, related_memory_id, quarantine_id
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    memory_id,
                    event_type,
                    source,
                    actor,
                    details,
                    created_at,
                    related_memory_id,
                    quarantine_id,
                ),
            )
            event_id = int(cursor.lastrowid)
        return ProvenanceEvent(
            event_id,
            memory_id,
            event_type,
            source,
            actor,
            details,
            created_at,
            related_memory_id,
            quarantine_id,
        )

    def history(self, memory_id: int) -> list[ProvenanceEvent]:
        with self._connect() as db:
            rows = db.execute(
                "SELECT * FROM memory_provenance WHERE memory_id = ? ORDER BY id ASC",
                (memory_id,),
            ).fetchall()
        return [self._from_row(row) for row in rows]
