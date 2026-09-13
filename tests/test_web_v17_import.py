def test_web_v17_imports_and_exposes_control_center():
    from hakham import web_v17

    assert web_v17.app is not None
    assert "v0.17 INSTAGRAM DIRECT" in web_v17.CONTROL_CENTER_HTML
