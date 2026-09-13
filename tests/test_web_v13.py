import httpx
import pytest
from fastapi import HTTPException

from hakham import web_v13


def test_reliable_whatsapp_requires_explicit_approval() -> None:
    request = web_v13.ReliableWhatsAppRequest(number="5585999999999", text="teste", approved=False)
    with pytest.raises(HTTPException) as exc:
        web_v13.send_whatsapp_reliable(request)
    assert exc.value.status_code == 403


def test_upstream_detail_extracts_evolution_message() -> None:
    response = httpx.Response(
        500,
        json={"status": 500, "response": {"message": "Connection Closed"}},
    )
    assert web_v13._safe_upstream_detail(response) == "Connection Closed"


def test_v13_html_keeps_privacy_vision_and_reliable_whatsapp() -> None:
    html = web_v13.CONTROL_CENTER_HTML
    assert "v0.13" in html
    assert "hakham-v13-wa-reliability" in html
    assert "/api/whatsapp/send-reliable" in html
    assert "#memoryPanel{display:none!important}" in html
    assert "VISÃO + MEMÓRIA" in html
