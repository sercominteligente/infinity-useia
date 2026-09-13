from hakham.working import WorkingMemory


def test_working_memory_is_bounded():
    memory = WorkingMemory(max_items=2)
    memory.set("a", "1")
    memory.set("b", "2")
    memory.set("c", "3")
    assert [item.key for item in memory.snapshot()] == ["b", "c"]


def test_working_memory_update_moves_key_to_latest():
    memory = WorkingMemory(max_items=3)
    memory.set("a", "1")
    memory.set("b", "2")
    memory.set("a", "3")
    assert [(item.key, item.value) for item in memory.snapshot()] == [("b", "2"), ("a", "3")]


def test_working_memory_clear():
    memory = WorkingMemory()
    memory.set("task", "build")
    memory.clear()
    assert memory.snapshot() == []
