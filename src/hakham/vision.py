from __future__ import annotations

import base64
import hashlib
import os
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

from .memory import MemoryStore


ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}
MAX_IMAGE_BYTES = 12 * 1024 * 1024


@dataclass(frozen=True)
class VisualMemory:
    id: int
    sha256: str
    filename: str
    mime_type: str
    local_path: str
    description: str
    context: str
    model: str
    created_at: str
    memory_id: int | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class VisualMemoryStore:
    """Durable registry for original images plus semantic visual descriptions."""

    def __init__(self, db_path: str = "data/hakham.db", asset_dir: str = "data/visual_memory") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.asset_dir = Path(asset_dir)
        self.asset_dir.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.db_path)
        db.row_factory = sqlite3.Row
        return db

    def _initialize(self) -> None:
        with self._connect() as db:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS visual_memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sha256 TEXT NOT NULL UNIQUE,
                    filename TEXT NOT NULL,
                    mime_type TEXT NOT NULL,
                    local_path TEXT NOT NULL,
                    description TEXT NOT NULL,
                    context TEXT NOT NULL DEFAULT '',
                    model TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    memory_id INTEGER
                )
                """
            )
            db.execute("CREATE INDEX IF NOT EXISTS idx_visual_created ON visual_memories(created_at)")

    @staticmethod
    def _from_row(row: sqlite3.Row) -> VisualMemory:
        return VisualMemory(
            id=int(row["id"]),
            sha256=str(row["sha256"]),
            filename=str(row["filename"]),
            mime_type=str(row["mime_type"]),
            local_path=str(row["local_path"]),
            description=str(row["description"]),
            context=str(row["context"]),
            model=str(row["model"]),
            created_at=str(row["created_at"]),
            memory_id=int(row["memory_id"]) if row["memory_id"] is not None else None,
        )

    def persist_image(self, image_bytes: bytes, mime_type: str) -> tuple[str, Path]:
        if mime_type not in ALLOWED_IMAGE_TYPES:
            raise ValueError(f"unsupported image type: {mime_type}")
        if not image_bytes:
            raise ValueError("empty image")
        if len(image_bytes) > MAX_IMAGE_BYTES:
            raise ValueError("image exceeds 12 MB limit")
        digest = hashlib.sha256(image_bytes).hexdigest()
        path = self.asset_dir / f"{digest}{ALLOWED_IMAGE_TYPES[mime_type]}"
        if not path.exists():
            path.write_bytes(image_bytes)
        return digest, path

    def save(
        self,
        *,
        sha256: str,
        filename: str,
        mime_type: str,
        local_path: str,
        description: str,
        context: str,
        model: str,
        memory_id: int | None,
    ) -> VisualMemory:
        created_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as db:
            existing = db.execute("SELECT * FROM visual_memories WHERE sha256 = ?", (sha256,)).fetchone()
            if existing is not None:
                db.execute(
                    "UPDATE visual_memories SET filename=?, description=?, context=?, model=?, memory_id=? WHERE sha256=?",
                    (filename, description, context, model, memory_id, sha256),
                )
                row = db.execute("SELECT * FROM visual_memories WHERE sha256 = ?", (sha256,)).fetchone()
                return self._from_row(row)
            cursor = db.execute(
                """
                INSERT INTO visual_memories(
                    sha256, filename, mime_type, local_path, description, context, model, created_at, memory_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (sha256, filename, mime_type, local_path, description, context, model, created_at, memory_id),
            )
            row = db.execute("SELECT * FROM visual_memories WHERE id = ?", (int(cursor.lastrowid),)).fetchone()
        return self._from_row(row)

    def recent(self, limit: int = 10) -> list[VisualMemory]:
        limit = max(1, min(int(limit), 50))
        with self._connect() as db:
            rows = db.execute("SELECT * FROM visual_memories ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [self._from_row(row) for row in rows]

    def search(self, query: str, limit: int = 10) -> list[VisualMemory]:
        query = query.strip()
        if not query:
            return self.recent(limit)
        limit = max(1, min(int(limit), 50))
        needle = f"%{query}%"
        with self._connect() as db:
            rows = db.execute(
                """
                SELECT * FROM visual_memories
                WHERE description LIKE ? OR context LIKE ? OR filename LIKE ?
                ORDER BY id DESC LIMIT ?
                """,
                (needle, needle, needle, limit),
            ).fetchall()
        return [self._from_row(row) for row in rows]


class OpenAIVisionClient:
    """Small multimodal client used only as HAKHAM's visual sensor."""

    def __init__(self, api_key: str, model: str = "gpt-5.6-luna", base_url: str = "https://api.openai.com/v1") -> None:
        self.api_key = api_key.strip()
        self.model = model.strip() or "gpt-5.6-luna"
        self.base_url = base_url.rstrip("/")

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    @staticmethod
    def _extract_text(payload: dict[str, Any]) -> str:
        direct = payload.get("output_text")
        if isinstance(direct, str) and direct.strip():
            return direct.strip()
        chunks: list[str] = []
        output = payload.get("output", [])
        if isinstance(output, list):
            for item in output:
                if not isinstance(item, dict):
                    continue
                content = item.get("content", [])
                if not isinstance(content, list):
                    continue
                for part in content:
                    if not isinstance(part, dict):
                        continue
                    text = part.get("text")
                    if isinstance(text, str) and text.strip():
                        chunks.append(text.strip())
        if not chunks:
            raise ValueError("vision response did not contain text")
        return "\n".join(chunks)

    def analyze(self, image_bytes: bytes, mime_type: str, *, context: str = "") -> str:
        if not self.configured:
            raise ValueError("OPENAI_API_KEY is required for visual analysis")
        encoded = base64.b64encode(image_bytes).decode("ascii")
        context_line = f"Contexto informado pelo Ach: {context.strip()}\n" if context.strip() else ""
        prompt = (
            "Você é o sensor visual do HAKHAM Infinity. Analise a imagem para memória de longo prazo. "
            "Responda em português do Brasil, de forma objetiva e factual. Descreva elementos visuais, textos legíveis, "
            "cores, composição, objetos, interface ou produto e detalhes úteis para reconhecer esta imagem no futuro. "
            "Quando for material de marca/design, registre também decisões visuais observáveis e possíveis inconsistências. "
            "Não identifique pessoas desconhecidas nem infira atributos sensíveis. Diferencie observação de hipótese.\n"
            f"{context_line}"
            "Finalize com uma linha iniciada por 'Chaves de memória:' contendo termos curtos para recuperação futura."
        )
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{self.base_url}/responses",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={
                    "model": self.model,
                    "input": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "input_text", "text": prompt},
                                {"type": "input_image", "image_url": f"data:{mime_type};base64,{encoded}", "detail": "high"},
                            ],
                        }
                    ],
                },
            )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("invalid vision response")
        return self._extract_text(payload)


class VisionService:
    def __init__(self) -> None:
        load_dotenv()
        memory_db = os.getenv("HAKHAM_MEMORY_DB", "data/hakham.db").strip() or "data/hakham.db"
        self.store = VisualMemoryStore(
            memory_db,
            os.getenv("HAKHAM_VISUAL_MEMORY_DIR", "data/visual_memory").strip() or "data/visual_memory",
        )
        self.memory = MemoryStore(memory_db)
        self.client = OpenAIVisionClient(
            os.getenv("OPENAI_API_KEY", ""),
            os.getenv("HAKHAM_VISION_MODEL", "gpt-5.6-luna"),
            os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        )

    @property
    def configured(self) -> bool:
        return self.client.configured

    def analyze_and_remember(self, image_bytes: bytes, mime_type: str, *, filename: str = "image", context: str = "") -> VisualMemory:
        sha256, path = self.store.persist_image(image_bytes, mime_type)
        description = self.client.analyze(image_bytes, mime_type, context=context)
        semantic = self.memory.remember(
            f"Memória visual: {filename}. {context.strip()}\n{description}".strip(),
            kind="entity",
            source="visual",
            importance=75,
            subject_key=f"visual:{sha256[:20]}",
        )
        return self.store.save(
            sha256=sha256,
            filename=(filename or "image")[:240],
            mime_type=mime_type,
            local_path=str(path),
            description=description,
            context=context.strip(),
            model=self.client.model,
            memory_id=semantic.id,
        )
