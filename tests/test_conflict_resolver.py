from hakham.conflict_resolver import MemoryConflictResolver
from hakham.memory import Memory


def memory(content: str, source: str, importance: int, created_at: str) -> Memory:
    return Memory(
        id=1,
        content=content,
        created_at=created_at,
        source=source,
        importance=importance,
    )


def test_same_content_is_deduplicated():
    resolver = MemoryConflictResolver()
    existing = memory("Use Ollama locally", "conversation", 70, "2026-09-01T00:00:00+00:00")
    candidate = memory(" use ollama locally ", "chatgpt-export", 80, "2026-09-08T00:00:00+00:00")
    decision = resolver.resolve(existing, candidate)
    assert decision.action == "deduplicate"
    assert decision.winner == "existing"


def test_explicit_user_memory_can_replace_weaker_historical_source():
    resolver = MemoryConflictResolver()
    existing = memory("Launch broadly", "chatgpt-export", 55, "2025-01-01T00:00:00+00:00")
    candidate = memory("Launch as a focused pilot", "user-explicit", 95, "2026-09-08T00:00:00+00:00")
    decision = resolver.resolve(existing, candidate)
    assert decision.action == "replace"
    assert decision.winner == "candidate"


def test_close_scores_require_review():
    resolver = MemoryConflictResolver()
    existing = memory("Option A", "github", 80, "2026-09-01T00:00:00+00:00")
    candidate = memory("Option B", "google-drive", 80, "2026-09-08T00:00:00+00:00")
    decision = resolver.resolve(existing, candidate)
    assert decision.action == "review"
    assert decision.winner == "none"
