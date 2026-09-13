from hakham import web_v12
from hakham.core import HakhamCore


def test_v12_hides_memory_panel_from_dashboard() -> None:
    html = web_v12.CONTROL_CENTER_HTML
    assert "Orbit Command v0.12 Stable Demo" in html
    assert "#memoryPanel{display:none!important}" in html
    assert "memory-nav-hidden" in html
    assert "WEB RESEARCH" in html
    assert "WHATSAPP CONTROL" in html
    assert "VISÃO + MEMÓRIA" in html


def test_core_exposes_visual_grounding_entrypoint() -> None:
    assert callable(getattr(HakhamCore, "observe_visual", None))
