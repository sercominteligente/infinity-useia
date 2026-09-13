from hakham.web_v19_2 import CONTROL_CENTER_HTML, app


def test_v19_2_embeds_reactor_and_adds_local_windows() -> None:
    assert app is not None
    assert "v0.19.2 EMBEDDED REACTOR" in CONTROL_CENTER_HTML
    assert "hakham-v19-2-embedded-reactor" in CONTROL_CENTER_HTML
    assert "AGENTES HAKHAM" in CONTROL_CENTER_HTML
    assert "TOOL GATEWAY" in CONTROL_CENTER_HTML
    assert "STATUS DO SISTEMA" in CONTROL_CENTER_HTML
    assert "MEMÓRIA HAKHAM" in CONTROL_CENTER_HTML
    assert "PROJETOS" in CONTROL_CENTER_HTML
    assert "data-kind=\"agents\"" in CONTROL_CENTER_HTML or "dataset.kind=spec.kind" in CONTROL_CENTER_HTML
    assert "'/api/agents'" in CONTROL_CENTER_HTML
    assert "'/api/tools'" in CONTROL_CENTER_HTML
    assert "'/api/status'" in CONTROL_CENTER_HTML
