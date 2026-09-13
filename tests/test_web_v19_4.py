from hakham.web_v19_4 import CONTROL_CENTER_HTML, app
from hakham.web_latest import app as latest_app


def test_v19_4_reactor_fusion_and_image_upload_are_present() -> None:
    assert app is not None
    assert latest_app is app
    assert "v0.19.4 REACTOR FUSION" in CONTROL_CENTER_HTML
    assert 'id="hakham-v19-4-reactor-fusion"' in CONTROL_CENTER_HTML
    assert 'id="hakham-v19-4-reactor-fusion-js"' in CONTROL_CENTER_HTML
    assert "width:min(99%,840px)" in CONTROL_CENTER_HTML
    assert "stroke-width:7.2" in CONTROL_CENTER_HTML
    assert "contextImageBtn" in CONTROL_CENTER_HTML
    assert "contextImageFile" in CONTROL_CENTER_HTML
    assert "Enviar imagem para Hakham" in CONTROL_CENTER_HTML
    assert "/api/vision/analyze" in CONTROL_CENTER_HTML
    assert 'data-kind="image"' in CONTROL_CENTER_HTML
    assert "12*1024*1024" in CONTROL_CENTER_HTML
    assert "clipboardData" in CONTROL_CENTER_HTML
    assert "dataTransfer" in CONTROL_CENTER_HTML
