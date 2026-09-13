from __future__ import annotations

from . import tool_gateway as tool_gateway_module
from .gemini_bridge import GeminiWebResearchService

# Preserve the existing search grounding adapter for the main chat.
tool_gateway_module.WebResearchService = GeminiWebResearchService

from . import web_v20 as release
from .superpowers import install

app = release.app
install(app)

# Add a navigation entry without replacing any existing routes or tools.
_NAV = '''<a href="/superpowers" style="position:fixed;bottom:18px;left:18px;z-index:10000;background:#153f50;color:#dcfff8;padding:10px 16px;border:1px solid #77ecdf;border-radius:12px;font:14px system-ui">Superpoderes: busca + avatar</a>'''
release._stable_web.CONTROL_CENTER_HTML = release._stable_web.CONTROL_CENTER_HTML.replace("</body>", _NAV + "</body>")
CONTROL_CENTER_HTML = release._stable_web.CONTROL_CENTER_HTML


def main() -> None:
    import uvicorn
    uvicorn.run("hakham.web_latest:app", host="127.0.0.1", port=8765, reload=False)


if __name__ == "__main__":
    main()
