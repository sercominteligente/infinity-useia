from types import SimpleNamespace

from hakham.command_router import CommandRouter


class FakeRuntime:
    def state(self):
        raise AssertionError("runtime should not be needed for /help or unknown commands")


def test_non_command_is_not_intercepted():
    result = CommandRouter(FakeRuntime()).handle("Shalom Hakham")
    assert result.handled is False


def test_help_lists_safe_commands():
    result = CommandRouter(FakeRuntime()).handle("/help")
    assert result.handled is True
    assert "/drive" in result.answer
    assert "/wa-status" in result.answer
    assert "/agent" in result.answer


def test_sensitive_whatsapp_command_does_not_auto_execute():
    result = CommandRouter(FakeRuntime()).handle("/wa-send 5585999999999 teste")
    assert result.handled is True
    assert "ação vermelha" in result.answer.casefold()
    assert "confirme" in result.answer.casefold() or "confirma" in result.answer.casefold()
