from __future__ import annotations

from . import tool_gateway as tool_gateway_module
from .gemini_bridge import GeminiWebResearchService

# ToolGateway imports WebResearchService by name, so patch that reference before
# the latest UI/runtime is imported. Contextual research cards keep the same UI,
# but their web.search executor can use Gemini Google Search grounding.
tool_gateway_module.WebResearchService = GeminiWebResearchService

from . import web_v20 as release


app = release.app
CONTROL_CENTER_HTML = release.CONTROL_CENTER_HTML


def main() -> None:
    import uvicorn

    uvicorn.run("hakham.web_latest:app", host="127.0.0.1", port=8765, reload=False)


if __name__ == "__main__":
    main()
