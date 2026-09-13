from hakham import web_v11


def test_research_cockpit_is_current() -> None:
    html = web_v11.CONTROL_CENTER_HTML
    assert "Orbit Command v0.11 Research" in html
    assert "WEB RESEARCH" in html
    assert 'data-tool="web.search"' in html or "web.search" in html
    assert "hakham-v11-research-js" in html
    assert "Pesquise na internet: " in html


def test_research_cockpit_keeps_demo_features() -> None:
    html = web_v11.CONTROL_CENTER_HTML
    assert "VISÃO + MEMÓRIA" in html
    assert "WHATSAPP CONTROL" in html
    assert "/assets/hakham-official?v=071" in html
