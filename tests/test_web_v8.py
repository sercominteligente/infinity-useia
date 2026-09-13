from hakham import web_v8


def test_avatar_endpoint_returns_official_png() -> None:
    response = web_v8.hakham_official()
    body = web_v8.HAKHAM_LOCAL_AVATAR.read_bytes()
    assert response.media_type == "image/png"
    assert body[:8] == b"\x89PNG\r\n\x1a\n"
    assert len(body) > 1024


def test_responsive_contract_is_present() -> None:
    # Later cockpit layers intentionally enhance the shared v8 HTML object at
    # import time, so this test protects the responsive contract rather than a
    # historical title string.
    html = web_v8.CONTROL_CENTER_HTML
    assert "Orbit Command" in html
    assert "hakham-v071-responsive" in html
    assert "@media(max-width:1280px)" in html
    assert "@media(max-width:900px)" in html
    assert "@media(max-width:640px)" in html
    assert "@media(max-width:420px)" in html
    assert ".stage{display:flex;flex-direction:column" in html
    assert ".compose textarea{grid-column:1/-1" in html
    assert "src=\"/assets/hakham-official?v=071\"" in html


def test_status_identifies_responsive_generation(monkeypatch) -> None:
    monkeypatch.setattr(web_v8.previous, "status", lambda: {"provider": "test", "model": "test"})
    payload = web_v8.status()
    assert payload["version"] == "0.7.1"
    assert payload["ui_generation"] == "orbit-command-responsive-v4"
