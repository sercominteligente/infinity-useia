from hakham.memory import MemoryStore


def test_memory_survives_restart(tmp_path):
    db_path = tmp_path / "hakham.db"

    first_process = MemoryStore(str(db_path))
    first_process.remember("Project Luna uses senior teacher agents.")

    second_process = MemoryStore(str(db_path))
    results = second_process.search("Luna")

    assert len(results) == 1
    assert "senior teacher agents" in results[0].content
