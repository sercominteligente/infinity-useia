from __future__ import annotations

import hashlib
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path


class MemoryKind(str, Enum):
    FACT = "fact"
    PROJECT = "project"
    DECISION = "decision"
    PREFERENCE = "preference"
    TASK = "task"
    ENTITY = "entity"
    CONVERSATION = "conversation"


class MemoryStatus(str, Enum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"


@dataclass(frozen=True)
class Memory:
    id: int
    content: str
    created_at: str
    kind: str = MemoryKind.CONVERSATION.value
    source: str = "conversation"
    importance: int = 50
    subject_key: str | None = None
    fingerprint: str | None = None
    status: str = MemoryStatus.ACTIVE.value
    supersedes_id: int | None = None


class MemoryStore:
    """Durable semantic memory for HAKHAM Infinity."""

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
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    kind TEXT NOT NULL DEFAULT 'conversation',
                    source TEXT NOT NULL DEFAULT 'conversation',
                    importance INTEGER NOT NULL DEFAULT 50,
                    subject_key TEXT,
                    fingerprint TEXT,
                    status TEXT NOT NULL DEFAULT 'active',
                    supersedes_id INTEGER
                )
                """
            )
            columns = {row[1] for row in db.execute("PRAGMA table_info(memories)")}
            migrations = {
                "kind": "ALTER TABLE memories ADD COLUMN kind TEXT NOT NULL DEFAULT 'conversation'",
                "source": "ALTER TABLE memories ADD COLUMN source TEXT NOT NULL DEFAULT 'conversation'",
                "importance": "ALTER TABLE memories ADD COLUMN importance INTEGER NOT NULL DEFAULT 50",
                "subject_key": "ALTER TABLE memories ADD COLUMN subject_key TEXT",
                "fingerprint": "ALTER TABLE memories ADD COLUMN fingerprint TEXT",
                "status": "ALTER TABLE memories ADD COLUMN status TEXT NOT NULL DEFAULT 'active'",
                "supersedes_id": "ALTER TABLE memories ADD COLUMN supersedes_id INTEGER",
            }
            for column, statement in migrations.items():
                if column not in columns:
                    db.execute(statement)
            db.execute("CREATE INDEX IF NOT EXISTS idx_memories_fingerprint ON memories(fingerprint)")
            db.execute("CREATE INDEX IF NOT EXISTS idx_memories_subject_status ON memories(subject_key, status)")

    @staticmethod
    def _normalize(text: str) -> str:
        text = text.casefold().strip()
        return re.sub(r"\s+", " ", text)

    @classmethod
    def _fingerprint(cls, content: str, kind: str) -> str:
        payload = f"{kind}:{cls._normalize(content)}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    @staticmethod
    def _from_row(row: sqlite3.Row) -> Memory:
        keys = set(row.keys())
        return Memory(
            id=int(row["id"]), content=row["content"], created_at=row["created_at"], kind=row["kind"],
            source=row["source"], importance=int(row["importance"]),
            subject_key=row["subject_key"] if "subject_key" in keys else None,
            fingerprint=row["fingerprint"] if "fingerprint" in keys else None,
            status=row["status"] if "status" in keys else MemoryStatus.ACTIVE.value,
            supersedes_id=row["supersedes_id"] if "supersedes_id" in keys else None,
        )

    def remember(self, content: str, *, kind: MemoryKind | str = MemoryKind.CONVERSATION,
                 source: str = "conversation", importance: int = 50,
                 subject_key: str | None = None, supersede_existing: bool = False) -> Memory:
        content = content.strip()
        if not content:
            raise ValueError("memory content cannot be empty")
        if not 0 <= importance <= 100:
            raise ValueError("importance must be between 0 and 100")
        kind_value = kind.value if isinstance(kind, MemoryKind) else str(kind)
        if kind_value not in {item.value for item in MemoryKind}:
            raise ValueError(f"unknown memory kind: {kind_value}")
        subject = self._normalize(subject_key) if subject_key else None
        fingerprint = self._fingerprint(content, kind_value)
        created_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as db:
            duplicate = db.execute("SELECT * FROM memories WHERE fingerprint = ? AND status = 'active' ORDER BY id DESC LIMIT 1", (fingerprint,)).fetchone()
            if duplicate is not None:
                return self._from_row(duplicate)
            supersedes_id: int | None = None
            if subject and supersede_existing:
                previous = db.execute("SELECT * FROM memories WHERE subject_key = ? AND kind = ? AND status = 'active' ORDER BY id DESC LIMIT 1", (subject, kind_value)).fetchone()
                if previous is not None:
                    supersedes_id = int(previous["id"])
                    db.execute("UPDATE memories SET status = 'superseded' WHERE id = ?", (supersedes_id,))
            cursor = db.execute("INSERT INTO memories(content, created_at, kind, source, importance, subject_key, fingerprint, status, supersedes_id) VALUES (?, ?, ?, ?, ?, ?, ?, 'active', ?)", (content, created_at, kind_value, source, importance, subject, fingerprint, supersedes_id))
            memory_id = int(cursor.lastrowid)
        return Memory(memory_id, content, created_at, kind_value, source, importance, subject, fingerprint, MemoryStatus.ACTIVE.value, supersedes_id)

    def recent(self, limit: int = 10, kind: MemoryKind | str | None = None, include_superseded: bool = False) -> list[Memory]:
        where: list[str] = []
        params: list[object] = []
        if not include_superseded:
            where.append("status = 'active'")
        if kind is not None:
            where.append("kind = ?")
            params.append(kind.value if isinstance(kind, MemoryKind) else str(kind))
        clause = f"WHERE {' AND '.join(where)}" if where else ""
        params.append(limit)
        with self._connect() as db:
            rows = db.execute(f"SELECT * FROM memories {clause} ORDER BY id DESC LIMIT ?", params).fetchall()
        return [self._from_row(row) for row in rows]

    def important(self, limit: int = 10, kind: MemoryKind | str | None = None) -> list[Memory]:
        where = ["status = 'active'"]
        params: list[object] = []
        if kind is not None:
            where.append("kind = ?")
            params.append(kind.value if isinstance(kind, MemoryKind) else str(kind))
        params.append(limit)
        with self._connect() as db:
            rows = db.execute(f"SELECT * FROM memories WHERE {' AND '.join(where)} ORDER BY importance DESC, id DESC LIMIT ?", params).fetchall()
        return [self._from_row(row) for row in rows]

    def search(self, query: str, limit: int = 5, kind: MemoryKind | str | None = None, include_superseded: bool = False) -> list[Memory]:
        query = query.strip()
        if not query:
            return self.recent(limit, kind, include_superseded)
        where = ["content LIKE ?"]
        params: list[object] = [f"%{query}%"]
        if not include_superseded:
            where.append("status = 'active'")
        if kind is not None:
            where.append("kind = ?")
            params.append(kind.value if isinstance(kind, MemoryKind) else str(kind))
        params.append(limit)
        with self._connect() as db:
            rows = db.execute(f"SELECT * FROM memories WHERE {' AND '.join(where)} ORDER BY importance DESC, id DESC LIMIT ?", params).fetchall()
        return [self._from_row(row) for row in rows]

    def history(self, subject_key: str, kind: MemoryKind | str | None = None) -> list[Memory]:
        subject = self._normalize(subject_key)
        where = ["subject_key = ?"]
        params: list[object] = [subject]
        if kind is not None:
            where.append("kind = ?")
            params.append(kind.value if isinstance(kind, MemoryKind) else str(kind))
        with self._connect() as db:
            rows = db.execute(f"SELECT * FROM memories WHERE {' AND '.join(where)} ORDER BY id DESC", params).fetchall()
        return [self._from_row(row) for row in rows]
