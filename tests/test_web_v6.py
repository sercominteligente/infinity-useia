from hakham.web_v6 import CONTROL_CENTER_HTML


def test_command_deck_v06_has_new_structural_layout() -> None:
    assert "HAKHAM // COMMAND DECK" in CONTROL_CENTER_HTML
    assert "command-grid" in CONTROL_CENTER_HTML
    assert "avatar-stage" in CONTROL_CENTER_HTML
    assert "CONSELHO DE AGENTES" in CONTROL_CENTER_HTML
    assert "TOOL GATEWAY" in CONTROL_CENTER_HTML
    assert "voiceCanvas" in CONTROL_CENTER_HTML
    assert "chatdock" in CONTROL_CENTER_HTML


def test_command_deck_v06_keeps_safe_tool_commands_visible() -> None:
    assert "/help mostra comandos" in CONTROL_CENTER_HTML
