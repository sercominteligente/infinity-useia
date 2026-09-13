import base64
from pathlib import Path

import hakham.web_v7 as web_v7


def _decoded(path: Path) -> bytes:
    return base64.b64decode(path.read_text(encoding="ascii").strip(), validate=True)


def test_official_v07_assets_are_valid_webp_payloads():
    for name in ("hakham-avatar-official.base64", "sercomtec-logo.base64"):
        data = _decoded(Path("assets") / name)
        assert data[:4] == b"RIFF"
        assert data[8:12] == b"WEBP"
        assert len(data) > 1000


def test_v07_asset_decoder_returns_webp_bytes():
    avatar = web_v7._decode_webp_asset("hakham-avatar-official.base64")
    logo = web_v7._decode_webp_asset("sercomtec-logo.base64")
    assert avatar[:4] == b"RIFF" and avatar[8:12] == b"WEBP"
    assert logo[:4] == b"RIFF" and logo[8:12] == b"WEBP"


def test_v07_html_enforces_readable_typography_and_layout():
    html = web_v7.CONTROL_CENTER_HTML
    assert "font-size:16px" in html
    assert "font-size:15px" in html
    assert "min-height:330px" in html
    assert 'src="/assets/hakham-official"' in html
    assert 'src="/assets/sercomtec-logo"' in html
    assert "VOICE REACTOR // GPT NATURAL" in html
    assert "github.status" in html
    assert "cloudflare.status" in html
