from __future__ import annotations

from . import web_v16 as integration_layer
from .instagram_direct import install_instagram_direct_patch


app = integration_layer.app
install_instagram_direct_patch()

INSTAGRAM_UI = r"""
<style id="hakham-v17-instagram">
.instagram-chip{display:inline-flex;align-items:center;gap:6px;margin-left:6px;padding:4px 9px;border:1px solid rgba(255,77,141,.34);border-radius:999px;background:rgba(70,13,42,.5);color:#ffb4d1;font-size:10px;font-weight:800;letter-spacing:.05em;white-space:nowrap}.instagram-chip:before{content:"";width:7px;height:7px;border-radius:50%;background:#ff4d8d;box-shadow:0 0 11px #ff4d8d}
@media(max-width:760px){.instagram-chip{font-size:9px}}
</style>
"""


def _enhance(html: str) -> str:
    html = html.replace("Orbit Command v0.16 Integration Gateway", "Orbit Command v0.17 Instagram Direct")
    html = html.replace("ORBIT COMMAND // v0.16 INTEGRATION GATEWAY", "ORBIT COMMAND // v0.17 INSTAGRAM DIRECT")
    html = html.replace("HAKHAM INFINITY ∞ v0.16 // SER Comtec", "HAKHAM INFINITY ∞ v0.17 // SER Comtec")
    html = html.replace("</head>", INSTAGRAM_UI + "\n</head>")
    marker = '<span class="integration-chip">6X CONNECT</span>'
    if marker in html and "INSTAGRAM DIRECT" not in html:
        html = html.replace(marker, marker + '<span class="instagram-chip">INSTAGRAM DIRECT</span>', 1)
    return html


# v0.16 is layered on top of v0.15 -> v0.14 -> v0.13 -> v0.12 -> web_v8.
# The actual HTML served by the FastAPI routes lives in that stable web_v8 module,
# so v0.17 must enhance that exact shared object instead of assuming web_v8 is a
# direct attribute of web_v15.
_stable_web = integration_layer.open_core_layer.commercial_layer.reliable_layer.stable_layer.web_v8
_stable_web.CONTROL_CENTER_HTML = _enhance(_stable_web.CONTROL_CENTER_HTML)
CONTROL_CENTER_HTML = _stable_web.CONTROL_CENTER_HTML


def main() -> None:
    import uvicorn

    uvicorn.run("hakham.web_v17:app", host="127.0.0.1", port=8765, reload=False)


if __name__ == "__main__":
    main()
