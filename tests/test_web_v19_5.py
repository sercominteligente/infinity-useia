def test_web_v19_5_exposes_cosmic_reactor_ui() -> None:
    from hakham import web_v19_5

    html = web_v19_5.CONTROL_CENTER_HTML
    assert "v0.19.5 COSMIC REACTOR" in html
    assert "hakhamCosmos" in html
    assert "cosmic-streak" in html
    assert "mask-image:linear-gradient" in html
    assert "width:min(110%,980px)" in html


def test_web_v19_5_module_remains_importable_after_newer_releases() -> None:
    from hakham import web_v19_5

    assert "v0.19.5 COSMIC REACTOR" in web_v19_5.CONTROL_CENTER_HTML
