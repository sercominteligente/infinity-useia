from hakham.web_v15 import CONTROL_CENTER_HTML


def test_open_core_layout_is_installed() -> None:
    html = CONTROL_CENTER_HTML
    assert "v0.15" in html
    assert "hakham-v15-open-core" in html
    assert 'id="hakhamCore"' in html
    assert 'id="chatPanel"' in html
    assert 'id="toolsPanel"' in html
    assert 'id="voiceScope"' in html
    assert "stage.appendChild(chat)" in html
    assert "left.appendChild(tools)" in html


def test_voice_reactor_and_avatar_motion_are_preserved() -> None:
    html = CONTROL_CENTER_HTML
    assert "VOICE REACTOR // GPT NATURAL" in html
    assert "animation:breathe" in html
    assert 'data-state="idle"' in html
    assert "speaking" in html
    assert "#voiceScope" in html
    assert "scope.style.width='100%'" in html
