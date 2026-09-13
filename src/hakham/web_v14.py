from __future__ import annotations

from . import web_v13 as reliable_layer
from .commercial_tools import install_commercial_tool_patch


install_commercial_tool_patch()
app = reliable_layer.app

COMMERCIAL_UI = r"""
<style id="hakham-v14-commercial">
.commercial-chip{display:inline-flex;align-items:center;gap:6px;margin-left:8px;padding:4px 9px;border:1px solid rgba(244,183,91,.34);border-radius:999px;background:rgba(49,31,5,.48);color:#ffd38a;font-size:10px;font-weight:800;letter-spacing:.05em;white-space:nowrap}
.commercial-chip:before{content:"";width:7px;height:7px;border-radius:50%;background:#f4b75b;box-shadow:0 0 11px #f4b75b}
@media(max-width:640px){.commercial-chip{font-size:9px;margin-left:4px}}
</style>
"""


def _enhance(html: str) -> str:
    html = html.replace("Orbit Command v0.13 Reliable WA", "Orbit Command v0.14 Commercial Core")
    html = html.replace("ORBIT COMMAND // v0.13 RELIABLE WA", "ORBIT COMMAND // v0.14 COMMERCIAL CORE")
    html = html.replace("HAKHAM INFINITY ∞ v0.13 // SER Comtec", "HAKHAM INFINITY ∞ v0.14 // SER Comtec")
    html = html.replace("</head>", COMMERCIAL_UI + "\n</head>")
    marker = '<span class="research-chip">WEB RESEARCH</span>'
    if marker in html and "COMMERCIAL CORE" not in html:
        html = html.replace(marker, marker + '<span class="commercial-chip">COMMERCIAL CORE</span>', 1)
    return html


reliable_layer.stable_layer.web_v8.CONTROL_CENTER_HTML = _enhance(
    reliable_layer.stable_layer.web_v8.CONTROL_CENTER_HTML
)
CONTROL_CENTER_HTML = reliable_layer.stable_layer.web_v8.CONTROL_CENTER_HTML


def main() -> None:
    import uvicorn

    uvicorn.run("hakham.web_v14:app", host="127.0.0.1", port=8765, reload=False)


if __name__ == "__main__":
    main()
