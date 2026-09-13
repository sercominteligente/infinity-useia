from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class Episode:
    id: int
    role: str
    content: str
    created_at: str
    session_id: str = "default"


class EpisodicStore:
    """Ordered conversational memory, separate from durable semantic memory."""

    VALID_ROLES = {"user", "assistant", "system", "tool"}

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
                CREATE TABLE IF NOT EXISTS episodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    session_id TEXT NOT NULL DEFAULT 'default'
                )
                """
            )
            db.execute(
                "CREATE INDEX IF NOT EXISTS idx_episodes_session_id ON episodes(session_id, id)"
            )

    @staticmethod
    def _from_row(row: sqlite3.Row) -> Episode:
        return Episode(
            id=int(row["id"]),
            role=row["role"],
            content=row["content"],
            created_at=row["created_at"],
            session_id=row["session_id"],
        )

    def append(self, role: str, content: str, *, session_id: str = "default") -> Episode:
        role = role.strip().casefold()
        content = content.strip()
        session_id = session_id.strip() or "default"
        if role not in self.VALID_ROLES:
            raise ValueError(f"unknown episode role: {role}")
        if not content:
            raise ValueError("episode content cannot be empty")
        created_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as db:
            cursor = db.execute(
                "INSERT INTO episodes(role, content, created_at, session_id) VALUES (?, ?, ?, ?)",
                (role, content, created_at, session_id),
            )
            episode_id = int(cursor.lastrowid)
        return Episode(episode_id, role, content, created_at, session_id)

    def recent(self, limit: int = 8, *, session_id: str = "default") -> list[Episode]:
        with self._connect() as db:
            rows = db.execute(
                "SELECT * FROM episodes WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                (session_id, limit),
            ).fetchall()
        return [self._from_row(row) for row in rows]
