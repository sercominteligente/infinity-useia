from __future__ import annotations

from . import web_v9 as vision_web
from . import web_v19_6 as previous
from .vision_router import EconomicalVisionService


app = previous.app

# v0.19.7 keeps the approved UI/cards intact and changes only the visual sensor.
# In auto mode the order is Gemini -> Abacus RouteLLM. OpenAI vision is used
# only when explicitly selected or when local config opts into that fallback.
vision_web.vision = EconomicalVisionService()


def _enhance(html: str) -> str:
    html = html.replace("Orbit Command v0.19.6 Precision Pass", "Orbit Command v0.19.7 Vision Router")
    html = html.replace("ORBIT COMMAND // v0.19.6 PRECISION PASS", "ORBIT COMMAND // v0.19.7 VISION ROUTER")
    html = html.replace("HAKHAM INFINITY ∞ v0.19.6 // SER Comtec", "HAKHAM INFINITY ∞ v0.19.7 // SER Comtec")
    return html


_stable_web = previous._stable_web
_stable_web.CONTROL_CENTER_HTML = _enhance(_stable_web.CONTROL_CENTER_HTML)
CONTROL_CENTER_HTML = _stable_web.CONTROL_CENTER_HTML


def main() -> None:
    import uvicorn

    uvicorn.run("hakham.web_v19_7:app", host="127.0.0.1", port=8765, reload=False)


if __name__ == "__main__":
    main()
