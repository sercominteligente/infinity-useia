from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class QuarantinedMemory:
    id: int
    content: str
    kind: str
    source: str
    importance: int
    subject_key: str | None
    reason: str
    status: str
    created_at: str
    reviewed_at: str | None = None
    review_note: str | None = None
    reviewed_by: str | None = None


class MemoryQuarantine:
    """Isolated review queue for uncertain or conflicting memory candidates."""

    VALID_REVIEW_STATUSES = {"approved", "rejected"}

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
                CREATE TABLE IF NOT EXISTS memory_quarantine (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    source TEXT NOT NULL,
                    importance INTEGER NOT NULL,
                    subject_key TEXT,
                    reason TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at TEXT NOT NULL,
                    reviewed_at TEXT,
                    review_note TEXT,
                    reviewed_by TEXT
                )
                """
            )
            columns = {row[1] for row in db.execute("PRAGMA table_info(memory_quarantine)")}
            if "reviewed_by" not in columns:
                db.execute("ALTER TABLE memory_quarantine ADD COLUMN reviewed_by TEXT")
            db.execute(
                "CREATE INDEX IF NOT EXISTS idx_memory_quarantine_status ON memory_quarantine(status, id)"
            )

    @staticmethod
    def _from_row(row: sqlite3.Row) -> QuarantinedMemory:
        keys = set(row.keys())
        return QuarantinedMemory(
            id=int(row["id"]),
            content=row["content"],
            kind=row["kind"],
            source=row["source"],
            importance=int(row["importance"]),
            subject_key=row["subject_key"],
            reason=row["reason"],
            status=row["status"],
            created_at=row["created_at"],
            reviewed_at=row["reviewed_at"],
            review_note=row["review_note"],
            reviewed_by=row["reviewed_by"] if "reviewed_by" in keys else None,
        )

    def add(
        self,
        content: str,
        *,
        kind: str,
        source: str,
        importance: int,
        reason: str,
        subject_key: str | None = None,
    ) -> QuarantinedMemory:
        content = content.strip()
        reason = reason.strip()
        if not content or not reason:
            raise ValueError("quarantine content and reason are required")
        if not 0 <= importance <= 100:
            raise ValueError("importance must be between 0 and 100")
        created_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as db:
            cursor = db.execute(
                """INSERT INTO memory_quarantine(
                       content, kind, source, importance, subject_key,
                       reason, status, created_at
                   ) VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)""",
                (content, kind, source, importance, subject_key, reason, created_at),
            )
            item_id = int(cursor.lastrowid)
        return QuarantinedMemory(
            item_id, content, kind, source, importance, subject_key,
            reason, "pending", created_at
        )

    def pending(self, limit: int = 100) -> list[QuarantinedMemory]:
        with self._connect() as db:
            rows = db.execute(
                "SELECT * FROM memory_quarantine WHERE status = 'pending' ORDER BY id ASC LIMIT ?",
                (limit,),
            ).fetchall()
        return [self._from_row(row) for row in rows]

    def get(self, item_id: int) -> QuarantinedMemory:
        with self._connect() as db:
            row = db.execute(
                "SELECT * FROM memory_quarantine WHERE id = ?", (item_id,)
            ).fetchone()
        if row is None:
            raise KeyError(f"quarantine item not found: {item_id}")
        return self._from_row(row)

    def review(
        self,
        item_id: int,
        *,
        status: str,
        note: str | None = None,
        reviewed_by: str | None = None,
    ) -> QuarantinedMemory:
        if status not in self.VALID_REVIEW_STATUSES:
            raise ValueError("status must be approved or rejected")
        reviewed_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as db:
            current = db.execute(
                "SELECT * FROM memory_quarantine WHERE id = ?", (item_id,)
            ).fetchone()
            if current is None:
                raise KeyError(f"quarantine item not found: {item_id}")
            if current["status"] != "pending":
                raise ValueError("quarantine item has already been reviewed")
            db.execute(
                """UPDATE memory_quarantine
                   SET status = ?, reviewed_at = ?, review_note = ?, reviewed_by = ?
                   WHERE id = ?""",
                (status, reviewed_at, note, reviewed_by, item_id),
            )
            row = db.execute(
                "SELECT * FROM memory_quarantine WHERE id = ?", (item_id,)
            ).fetchone()
        return self._from_row(row)
