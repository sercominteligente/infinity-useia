import base64


def test_web_v19_8_exposes_manual_field_vision() -> None:
    from hakham import web_v19_8

    html = web_v19_8.CONTROL_CENTER_HTML
    assert "v0.19.8 FIELD VISION PHASE 1" in html
    assert "fieldCameraBtn" in html
    assert "fieldCameraSwitch" in html
    assert "fieldCameraRemember" in html
    assert "/api/vision/live/analyze" in html
    assert "facingMode" in html
    assert "Nenhum vídeo é enviado continuamente" in html


def test_live_vision_can_analyze_without_persisting(monkeypatch) -> None:
    from hakham import web_v19_8

    class FakeClient:
        configured = True
        model = "fake-vision"

        def analyze(self, image_bytes: bytes, mime_type: str, *, context: str = "") -> str:
            assert image_bytes == b"field-frame"
            assert mime_type == "image/jpeg"
            return "Leitura temporária do ambiente."

    class FakeService:
        configured = True
        client = FakeClient()
        active_provider = "fake"

        def analyze_and_remember(self, *args, **kwargs):
            raise AssertionError("temporary field vision must not persist")

    monkeypatch.setattr(web_v19_8.vision_web, "vision", FakeService())
    data = base64.b64encode(b"field-frame").decode("ascii")
    request = web_v19_8.LiveVisionRequest(
        data_url=f"data:image/jpeg;base64,{data}",
        context="visita técnica",
        remember=False,
    )
    result = web_v19_8.analyze_live_vision(request)
    assert result["saved"] is False
    assert result["answer"] == "Leitura temporária do ambiente."
    assert result["provider"] == "fake"
