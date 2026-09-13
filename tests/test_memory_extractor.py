from hakham.memory import MemoryKind
from hakham.memory_extractor import MemoryExtractor


def test_extracts_decision_with_high_importance():
    extractor = MemoryExtractor()
    items = extractor.extract("Decidimos que o HAKHAM Infinity vai usar OpenJarvis como base.")
    assert items[0].kind == MemoryKind.DECISION
    assert items[0].importance == 90


def test_extracts_preference():
    extractor = MemoryExtractor()
    items = extractor.extract("Prefiro usar modelos locais quando possível.")
    assert items[0].kind == MemoryKind.PREFERENCE


def test_extracts_task():
    extractor = MemoryExtractor()
    items = extractor.extract("Precisamos criar o gateway do WhatsApp.")
    assert items[0].kind == MemoryKind.TASK


def test_ignores_low_signal_chat():
    extractor = MemoryExtractor()
    assert extractor.extract("kkkk ficou top") == []


def test_preserves_source():
    extractor = MemoryExtractor()
    items = extractor.extract("O projeto Portal Luna usa agentes professores.", source="chatgpt-export")
    assert items[0].source == "chatgpt-export"
