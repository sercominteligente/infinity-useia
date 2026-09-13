from __future__ import annotations

from fastapi import HTTPException

from . import web as backend
from .command_router import CommandRouter
from .web_v5 import CONTROL_CENTER_HTML, app


# Replace only the chat route from v0.5. All other tested routes/UI stay intact.
app.router.routes[:] = [
    route
    for route in app.router.routes
    if not (getattr(route, "path", None) == "/api/chat" and "POST" in (getattr(route, "methods", set()) or set()))
]
commands = CommandRouter(backend.runtime)


@app.post("/api/chat")
def chat(request: backend.ChatRequest) -> dict[str, str]:
    message = request.message.strip()
    command = commands.handle(message)
    if command.handled:
        return {"answer": command.answer}
    try:
        return backend.chat(request)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Hakham engine unavailable: {exc}") from exc


def main() -> None:
    import uvicorn

    uvicorn.run("hakham.web_v5_runtime:app", host="127.0.0.1", port=8765, reload=False)
