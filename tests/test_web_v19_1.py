from hakham.web_latest import app as latest_app
from hakham.web_v19_1 import CONTROL_CENTER_HTML, app


def test_v19_1_contextual_workspace_and_reactor_are_present() -> None:
    assert app is not None
    assert latest_app is app
    assert "v0.19.1 INFINITY REACTOR" in CONTROL_CENTER_HTML
    assert 'id="contextWorkspace"' in CONTROL_CENTER_HTML
    assert 'id="contextMinibar"' in CONTROL_CENTER_HTML
    assert "infinityReactor" in CONTROL_CENTER_HTML
    assert "INFINITY REACTOR // PRONTO" in CONTROL_CENTER_HTML
    assert "INSTAGRAM DIRECT" in CONTROL_CENTER_HTML
    assert "LIVE RESEARCH" in CONTROL_CENTER_HTML
    assert "WHATSAPP" in CONTROL_CENTER_HTML
    assert "COMMERCIAL CORE" in CONTROL_CENTER_HTML
    assert "data-state=\"listening\"" in CONTROL_CENTER_HTML
    assert "data-state=\"speaking\"" in CONTROL_CENTER_HTML
