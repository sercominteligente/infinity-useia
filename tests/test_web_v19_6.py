def test_web_v19_6_precision_ui_keeps_context_cards_and_moves_reactor() -> None:
    from hakham import web_v19_6

    html = web_v19_6.CONTROL_CENTER_HTML
    assert "v0.19.6 PRECISION PASS" in html
    assert "bottom:-10.5%" in html
    assert "top:auto" in html
    assert "hakham-v19-6-precision-pass" in html
    assert "hakhamCosmos" in html
    # Existing contextual workspace must remain available.
    assert "contextWorkspace" in html
    assert "cw-closing" in html


def test_web_v19_6_restores_natural_voice_preference() -> None:
    from hakham import web_v19_6

    html = web_v19_6.CONTROL_CENTER_HTML
    assert "hakhamVoiceEngine='openai'" in html
    assert "Fallback de voz do Windows foi bloqueado" in html
    assert "hakhamVoiceHealth" in html


def test_gemini_bridge_parses_candidate_text_without_network() -> None:
    from hakham.gemini_bridge import _candidate_text

    payload = {
        "candidates": [
            {"content": {"parts": [{"text": "primeiro"}, {"text": "segundo"}]}}
        ]
    }
    assert _candidate_text(payload) == "primeiro\nsegundo"
