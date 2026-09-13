def test_abacus_vision_parser_handles_openai_compatible_response() -> None:
    from hakham.vision_router import _abacus_text

    payload = {"choices": [{"message": {"content": "Imagem analisada."}}]}
    assert _abacus_text(payload) == "Imagem analisada."


def test_economy_vision_auto_prefers_abacus_when_gemini_is_missing(monkeypatch, tmp_path) -> None:
    from hakham.vision_router import EconomicalVisionService

    monkeypatch.setenv("HAKHAM_MEMORY_DB", str(tmp_path / "hakham.db"))
    monkeypatch.setenv("HAKHAM_VISUAL_MEMORY_DIR", str(tmp_path / "visual"))
    monkeypatch.setenv("HAKHAM_VISION_PROVIDER", "auto")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("ABACUS_ROUTELLM_API_KEY", "test-abacus-key")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("HAKHAM_VISION_ALLOW_OPENAI_FALLBACK", "false")

    service = EconomicalVisionService()
    assert service.configured is True
    assert service.client.provider_chain == ["abacus"]
    assert service.active_provider == "abacus"


def test_web_v19_7_keeps_cards_and_routes_vision() -> None:
    from hakham import web_v19_7

    html = web_v19_7.CONTROL_CENTER_HTML
    assert "v0.19.7 VISION ROUTER" in html
    assert "contextWorkspace" in html
    assert "cw-closing" in html
