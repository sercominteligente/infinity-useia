from hakham.importers.chatgpt_export import ChatGPTExportImporter, ImportedTurn
from hakham.memory import MemoryKind


def test_importer_extracts_only_user_memory_candidates():
    importer = ChatGPTExportImporter()
    turns = [
        ImportedTurn("c1", "user", "Decidimos que o projeto HAKHAM Infinity usará memória persistente."),
        ImportedTurn("c1", "assistant", "Combinado, vou lembrar disso."),
    ]

    items = importer.extract_candidates(turns)
    assert len(items) == 1
    assert items[0].kind == MemoryKind.DECISION
    assert items[0].source == "chatgpt-export"


def test_importer_ignores_low_signal_turns():
    importer = ChatGPTExportImporter()
    turns = [ImportedTurn("c1", "user", "kkkk ficou top")]
    assert importer.extract_candidates(turns) == []
