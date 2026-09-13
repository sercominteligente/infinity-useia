from __future__ import annotations

from fastapi import FastAPI, Query
from pathlib import Path
from fastapi.responses import HTMLResponse, Response, FileResponse
from . import web_v7 as previous

app = FastAPI(title="HAKHAM Infinity Control Center", version="0.7.1")
HAKHAM_LOCAL_AVATAR = Path(__file__).resolve().parent / "assets" / "hakham-official.png"

RESPONSIVE_CSS = r"""
<style id="hakham-v071-responsive">
/* v0.7.1: avatar + responsive hardening. Keep operational text comfortably readable. */
body{font-size:15px}
.page{width:min(1920px,100%);padding:18px clamp(14px,1.35vw,26px) 38px}
.stage{grid-template-columns:minmax(300px,.82fr) minmax(560px,1.45fr) minmax(320px,.88fr);gap:clamp(14px,1.1vw,20px)}
.panel{padding:18px;min-width:0}.panel-head h3{font-size:15px}.row,.statusline{font-size:14px}.row small,.agent small,.tool small{font-size:12px}
.core{min-width:0;min-height:730px;padding:20px clamp(14px,1.5vw,26px)}
.avatar-shell{width:min(680px,100%);height:490px;overflow:visible}
.avatar{height:min(470px,46vw);max-height:470px;width:auto;max-width:96%;object-fit:contain;object-position:center bottom;opacity:1;visibility:visible}
.synth{width:min(760px,100%)}.scope{height:118px}
.chat{min-height:360px;padding:20px}.chatlog{height:235px}.bubble{font-size:15px}.compose textarea{font-size:16px;min-height:74px}
.topbar{padding-inline:clamp(12px,1.2vw,22px)}

@media(max-width:1550px){
  .topbar{grid-template-columns:auto minmax(420px,1fr) auto;gap:12px}
  .brandbar{min-width:285px;gap:12px}.hakham-brand b{font-size:16px}.brand-infinity{font-size:34px}.sercomtec{max-width:145px}
  .topcenter{grid-template-columns:auto minmax(220px,1fr);gap:10px}.menu button{padding:8px 8px}
  .stage{grid-template-columns:minmax(260px,.78fr) minmax(500px,1.34fr) minmax(285px,.82fr);gap:14px}
  .core{min-height:690px}.avatar-shell{height:445px}.avatar{height:425px}.orbit{width:365px;height:365px}
  .agent-grid{grid-template-columns:1fr 1fr}
}

@media(max-width:1280px){
  .topbar{position:sticky;grid-template-columns:1fr auto;align-items:center}
  .brandbar{min-width:0}.topcenter{grid-column:1/-1;grid-row:2;grid-template-columns:auto minmax(260px,1fr)}
  .topright{grid-column:2;grid-row:1;justify-content:flex-end}.clock{display:none}
  .stage{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}
  .stage>.core{grid-column:1/-1;grid-row:1;min-height:690px}
  .stage>.left{grid-column:1;grid-row:2}.stage>.right{grid-column:2;grid-row:2;display:grid;grid-template-columns:1fr}
  .avatar-shell{height:455px}.avatar{height:440px;max-width:min(620px,92vw)}
  .chat{margin-top:16px}
}

@media(max-width:900px){
  .topbar{position:relative;display:grid;grid-template-columns:1fr;gap:10px;padding:12px}
  .brandbar,.topcenter,.topright{grid-column:1;grid-row:auto;width:100%}
  .brandbar{justify-content:space-between}.topcenter{grid-template-columns:1fr}.menu{order:2;display:grid;grid-template-columns:repeat(5,minmax(0,1fr));width:100%}.menu button{padding:9px 5px;font-size:12px}
  .topright{justify-content:space-between;flex-wrap:wrap}.engine{margin-left:auto}.search input{height:48px}
  .page{padding:12px}
  .stage{display:flex;flex-direction:column;gap:14px}
  .stage>.core{order:1;width:100%;min-height:650px}.stage>.left{order:2;width:100%}.stage>.right{order:3;width:100%}
  .left,.right{display:grid;grid-template-columns:1fr 1fr;gap:12px}.left>#projectsPanel{grid-column:1/-1}.right>#toolsPanel{grid-column:1/-1}
  .avatar-shell{height:420px}.avatar{height:405px;max-width:92vw}.orbit{width:340px;height:340px}
  .chat{min-height:390px}.chatlog{height:250px}
}

@media(max-width:640px){
  body{font-size:15px}.page{padding:8px}.topbar{padding:10px 8px}
  .brandbar{gap:8px;flex-wrap:nowrap}.brand-divider{display:none}.hakham-brand b{font-size:15px;letter-spacing:.08em}.hakham-brand small{font-size:11px}.brand-infinity{font-size:31px}.sercomtec{height:28px;max-width:125px}
  .menu{grid-template-columns:repeat(3,1fr)}.menu button:nth-child(4),.menu button:nth-child(5){grid-column:auto}
  .topright{gap:7px}.mode-group{width:100%;justify-content:center}.modebtn{flex:1;padding:8px 7px}.engine{width:100%;margin:0}.clock{display:none}
  .left,.right{grid-template-columns:1fr}.left>#projectsPanel,.right>#toolsPanel{grid-column:auto}
  .float{border-radius:15px}.panel{padding:15px}.core{min-height:575px;padding:16px 8px}.core-title h1{font-size:clamp(25px,8vw,34px)}.core-title p{font-size:13px;padding-inline:6px}
  .avatar-shell{height:335px;margin-top:0}.avatar{height:320px;max-width:96vw}.orbit{width:270px;height:270px}.orbit:before{inset:18px}.orbit:after{inset:-24px}.energy-disc{width:260px;height:72px}
  .synth{width:100%}.scope{height:92px}.synth-head{font-size:12px}.synth-head b{font-size:13px}.voicebtn,.action{font-size:13px;padding:10px}
  .agent-grid{grid-template-columns:1fr 1fr}.tool-grid{max-height:none}
  .chat{margin-top:12px;min-height:430px;padding:15px 12px}.chat-head{align-items:flex-start}.chat-head h2{font-size:17px}.chatlog{height:275px}.bubble{max-width:96%;font-size:15px;padding:11px 12px}.compose{grid-template-columns:1fr 52px}.compose textarea{grid-column:1/-1;min-height:88px;font-size:16px}.compose .send{grid-column:1;min-height:50px}.compose button:not(.send){grid-column:2;grid-row:2;min-width:52px}.footer{flex-direction:column;font-size:12px}
}

@media(max-width:420px){
  .hakham-brand small{display:none}.sercomtec{max-width:108px;height:25px}.menu{grid-template-columns:repeat(2,1fr)}
  .avatar-shell{height:300px}.avatar{height:288px}.orbit{width:240px;height:240px}
  .agent-grid{grid-template-columns:1fr}.voice-controls{display:grid;grid-template-columns:1fr 1fr}.voice-controls .voicebtn:last-child{grid-column:1/-1}
  .bubble{max-width:100%}.chatlog{height:300px}
}
</style>
"""


def _build_html() -> str:
    html = previous.CONTROL_CENTER_HTML
    html = html.replace("Orbit Command v0.7", "Orbit Command v0.7.1")
    html = html.replace("ORBIT COMMAND // v0.7", "ORBIT COMMAND // v0.7.1")
    html = html.replace("HAKHAM INFINITY ∞ v0.7 // SER Comtec", "HAKHAM INFINITY ∞ v0.7.1 // SER Comtec")
    html = html.replace('src="/assets/hakham-official"', 'src="/assets/hakham-official?v=071" onerror="this.onerror=null;this.style.opacity=.18;document.getElementById(\'avatarState\').textContent=\'AVATAR INDISPONÍVEL\'"')
    html = html.replace('src="/assets/sercomtec-logo"', 'src="/assets/sercomtec-logo?v=071"')
    return html.replace("</head>", RESPONSIVE_CSS + "\n</head>")


CONTROL_CENTER_HTML = _build_html()


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return CONTROL_CENTER_HTML


@app.get("/assets/hakham-official")
def hakham_official() -> FileResponse:
    return FileResponse(
        HAKHAM_LOCAL_AVATAR,
        media_type="image/png",
        headers={"Cache-Control": "no-store, max-age=0"},
    )


@app.get("/assets/sercomtec-logo")
def sercomtec_logo() -> Response:
    response = previous.sercomtec_logo()
    response.headers["Cache-Control"] = "no-store, max-age=0"
    return response


@app.get("/api/status")
def status() -> dict[str, object]:
    payload = previous.status()
    payload.update({"version": "0.7.1", "ui_generation": "orbit-command-responsive-v4"})
    return payload


@app.get("/api/memory/recent")
def recent_memory(limit: int = Query(default=8, ge=1, le=50)) -> dict[str, object]:
    return previous.recent_memory(limit)


@app.get("/api/projects")
def projects(limit: int = Query(default=6, ge=1, le=30)) -> dict[str, object]:
    return previous.projects(limit)


@app.get("/api/tasks")
def tasks(limit: int = Query(default=6, ge=1, le=30)) -> dict[str, object]:
    return previous.tasks(limit)


@app.get("/api/memory/search")
def search_memory(q: str = Query(default="", max_length=500), limit: int = Query(default=8, ge=1, le=50)) -> dict[str, object]:
    return previous.search_memory(q=q, limit=limit)


@app.post("/api/memory")
def create_memory(request: previous.backend.ManualMemoryRequest) -> dict[str, object]:
    return previous.create_memory(request)


@app.get("/api/models")
def models() -> dict[str, object]:
    return previous.models()


@app.post("/api/mode")
def set_mode(request: previous.backend.ModeRequest) -> dict[str, object]:
    return previous.set_mode(request)


@app.post("/api/chat")
def chat(request: previous.backend.ChatRequest) -> dict[str, str]:
    return previous.chat(request)


@app.post("/api/voice/speech")
def speech(request: previous.web_v4.SpeechRequest) -> Response:
    return previous.speech(request)


@app.get("/api/agents")
def list_agents() -> dict[str, object]:
    return previous.list_agents()


@app.post("/api/agents/delegate")
def delegate_agent(request: previous.web_v5.AgentTaskRequest) -> dict[str, object]:
    return previous.delegate_agent(request)


@app.get("/api/tools")
def list_tools() -> dict[str, object]:
    return previous.list_tools()


@app.post("/api/tools/execute")
def execute_tool(request: previous.web_v5.ToolExecuteRequest) -> dict[str, object]:
    return previous.execute_tool(request)


def main() -> None:
    import uvicorn

    uvicorn.run("hakham.web_v8:app", host="127.0.0.1", port=8765, reload=False)
