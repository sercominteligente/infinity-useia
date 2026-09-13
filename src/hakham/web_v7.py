from __future__ import annotations

import base64
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, Response

from . import web as backend
from . import web_v4
from . import web_v5
from . import web_v6 as previous
from .command_router import CommandRouter
from .tool_gateway import ToolGateway

app = FastAPI(title="HAKHAM Infinity Control Center", version="0.7.0")

ASSET_DIR = Path("assets")


def _decode_webp_asset(filename: str) -> bytes:
    path = ASSET_DIR / filename
    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"asset not installed: {filename}")
    try:
        payload = base64.b64decode(path.read_text(encoding="ascii").strip(), validate=True)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"invalid asset payload: {filename}") from exc
    if len(payload) < 12 or payload[:4] != b"RIFF" or payload[8:12] != b"WEBP":
        raise HTTPException(status_code=500, detail=f"invalid WebP asset: {filename}")
    return payload


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return CONTROL_CENTER_HTML


@app.get("/assets/hakham-official")
def hakham_official() -> Response:
    return Response(
        _decode_webp_asset("hakham-avatar-official.base64"),
        media_type="image/webp",
        headers={"Cache-Control": "no-cache"},
    )


@app.get("/assets/sercomtec-logo")
def sercomtec_logo() -> Response:
    return Response(
        _decode_webp_asset("sercomtec-logo.base64"),
        media_type="image/webp",
        headers={"Cache-Control": "no-cache"},
    )


@app.get("/api/status")
def status() -> dict[str, object]:
    payload = previous.status()
    gateway = ToolGateway()
    payload.update(
        {
            "version": "0.7.0",
            "ui_generation": "orbit-command-v3",
            "official_avatar_ready": (ASSET_DIR / "hakham-avatar-official.base64").is_file(),
            "sercomtec_logo_ready": (ASSET_DIR / "sercomtec-logo.base64").is_file(),
            "tool_count": len(gateway.specs()),
            "tool_configured_count": gateway.summary()["configured"],
        }
    )
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
def create_memory(request: backend.ManualMemoryRequest) -> dict[str, object]:
    return previous.create_memory(request)


@app.get("/api/models")
def models() -> dict[str, object]:
    return previous.models()


@app.post("/api/mode")
def set_mode(request: backend.ModeRequest) -> dict[str, object]:
    return previous.set_mode(request)


@app.post("/api/chat")
def chat(request: backend.ChatRequest) -> dict[str, str]:
    message = request.message.strip()
    if message.startswith("/"):
        result = CommandRouter(backend.runtime).handle(message)
        if result.handled:
            return {"answer": result.answer}
    return previous.chat(request)


@app.post("/api/voice/speech")
def speech(request: web_v4.SpeechRequest) -> Response:
    return web_v4.speech(request)


@app.get("/api/agents")
def list_agents() -> dict[str, object]:
    return web_v5.list_agents()


@app.post("/api/agents/delegate")
def delegate_agent(request: web_v5.AgentTaskRequest) -> dict[str, object]:
    return web_v5.delegate_agent(request)


@app.get("/api/tools")
def list_tools() -> dict[str, object]:
    return ToolGateway().summary()


@app.post("/api/tools/execute")
def execute_tool(request: web_v5.ToolExecuteRequest) -> dict[str, object]:
    return web_v5.execute_tool(request)


def main() -> None:
    import uvicorn

    uvicorn.run("hakham.web_v7:app", host="127.0.0.1", port=8765, reload=False)


CONTROL_CENTER_HTML = r"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>HAKHAM Infinity // Orbit Command v0.7</title>
<style>
:root{color-scheme:dark;--space:#01040b;--space2:#020a15;--panel:rgba(5,18,34,.66);--panel2:rgba(7,28,48,.58);--line:rgba(49,205,255,.28);--line2:rgba(52,126,168,.24);--cyan:#25dcff;--cyan2:#8df4ff;--blue:#248dff;--gold:#f4b75b;--green:#27e0ad;--red:#ff647b;--violet:#9a70ff;--text:#ecf9ff;--muted:#94afc0;--shadow:0 20px 55px rgba(0,0,0,.34)}
*{box-sizing:border-box}html{background:var(--space);font-size:16px}body{margin:0;min-height:100vh;color:var(--text);font:14px/1.5 Inter,Segoe UI,Arial,sans-serif;background:radial-gradient(circle at 50% 8%,rgba(16,101,151,.28),transparent 25%),radial-gradient(circle at 8% 42%,rgba(25,79,136,.20),transparent 26%),radial-gradient(circle at 92% 56%,rgba(71,40,128,.17),transparent 25%),radial-gradient(circle at 54% 76%,rgba(0,178,255,.08),transparent 24%),linear-gradient(180deg,#010611 0%,#01040b 58%,#00030a 100%);overflow-x:hidden}body:before,body:after{content:"";position:fixed;inset:0;pointer-events:none;z-index:-1;opacity:.62}body:before{background-image:radial-gradient(circle,#b9eeff 0 1px,transparent 1.4px),radial-gradient(circle,#5ca8ff 0 1px,transparent 1.5px),radial-gradient(circle,#fff 0 .7px,transparent 1px);background-size:137px 137px,211px 211px,79px 79px;background-position:13px 27px,61px 19px,7px 43px;animation:stars 90s linear infinite}body:after{background:radial-gradient(ellipse at 60% 27%,rgba(0,204,255,.075),transparent 28%),radial-gradient(ellipse at 30% 68%,rgba(128,69,255,.05),transparent 26%);filter:blur(18px)}button,input,textarea{font:inherit}button{color:inherit}a{color:inherit}@keyframes stars{to{transform:translate3d(-75px,45px,0)}}@keyframes breathe{0%,100%{transform:translateY(3px) scale(1)}50%{transform:translateY(-4px) scale(1.012)}}@keyframes listen{0%,100%{transform:scale(1.015) rotate(-.4deg)}50%{transform:scale(1.035) rotate(.5deg)}}@keyframes think{0%,100%{transform:translateY(2px)}50%{transform:translateY(-6px) rotate(.35deg)}}@keyframes speak{0%,100%{transform:translateY(2px) scale(1.015)}50%{transform:translateY(-3px) scale(1.028)}}@keyframes ring{to{transform:rotate(360deg)}}@keyframes pulse{0%,100%{opacity:.35;transform:scale(.98)}50%{opacity:.8;transform:scale(1.02)}}
.topbar{position:sticky;top:0;z-index:50;min-height:82px;padding:10px 20px;display:grid;grid-template-columns:auto minmax(360px,1fr) auto;gap:18px;align-items:center;background:rgba(1,7,16,.84);backdrop-filter:blur(22px) saturate(130%);border-bottom:1px solid rgba(36,206,255,.24);box-shadow:0 10px 38px rgba(0,0,0,.28)}.brandbar{display:flex;align-items:center;gap:17px;min-width:330px}.hakham-brand{display:flex;align-items:center;gap:10px}.brand-infinity{font-size:38px;line-height:1;color:var(--cyan);text-shadow:0 0 25px rgba(37,220,255,.65)}.hakham-brand b{font-size:18px;letter-spacing:.12em;white-space:nowrap}.hakham-brand small{display:block;font-size:12px;color:var(--cyan);letter-spacing:.08em;margin-top:1px}.brand-divider{width:1px;height:40px;background:linear-gradient(transparent,var(--line),transparent)}.sercomtec{height:34px;width:auto;max-width:180px;object-fit:contain;filter:drop-shadow(0 0 10px rgba(118,208,255,.18))}.ser-fallback{display:none;font-size:16px;font-weight:700;color:#d6eaff}.topcenter{min-width:0;display:grid;grid-template-columns:auto minmax(240px,1fr);gap:16px;align-items:center}.menu{display:flex;gap:5px;flex-wrap:wrap}.menu button{border:1px solid transparent;background:transparent;border-radius:9px;padding:9px 11px;font-size:13px;color:#9eb9c9;cursor:pointer;transition:.18s}.menu button:hover,.menu button.active{border-color:var(--line);background:rgba(7,42,65,.58);color:#fff}.search{position:relative;min-width:0}.search input{width:100%;height:44px;border-radius:12px;border:1px solid rgba(39,174,224,.34);background:rgba(3,17,31,.72);color:#e8f9ff;padding:0 48px 0 42px;outline:none;font-size:14px;box-shadow:inset 0 0 24px rgba(11,144,205,.06)}.search:before{content:"⌕";position:absolute;left:14px;top:7px;font-size:23px;color:#79bedc}.search .kbd{position:absolute;right:9px;top:11px;border:1px solid #24536d;border-radius:6px;padding:2px 6px;font-size:12px;color:#7895a7}.topright{display:flex;align-items:center;gap:10px;justify-content:flex-end}.mode-group{display:flex;gap:5px;padding:4px;border:1px solid rgba(36,138,187,.28);border-radius:10px;background:rgba(4,19,32,.62)}.modebtn{border:1px solid transparent;border-radius:7px;background:transparent;padding:7px 10px;font-size:12px;color:#86a7ba;cursor:pointer}.modebtn.active{background:var(--cyan);color:#001019;font-weight:800;box-shadow:0 0 20px rgba(37,220,255,.22)}.modebtn:disabled{opacity:.32;cursor:not-allowed}.engine{min-width:126px;text-align:center;padding:8px 10px;border:1px solid rgba(31,177,226,.35);border-radius:999px;background:rgba(5,26,43,.64);font-size:12px;color:#bdefff}.clock{min-width:73px;text-align:right;line-height:1.1}.clock small{display:block;font-size:12px;color:#849fb0}.clock b{font-size:18px}
.page{width:min(1900px,100%);margin:0 auto;padding:18px 20px 34px}.stage{display:grid;grid-template-columns:minmax(280px,.78fr) minmax(500px,1.35fr) minmax(300px,.82fr);gap:18px;align-items:start}.stack{display:grid;gap:16px}.float{position:relative;overflow:hidden;border:1px solid var(--line);border-radius:18px;background:linear-gradient(145deg,rgba(7,24,42,.70),rgba(2,10,20,.58));backdrop-filter:blur(18px) saturate(125%);box-shadow:var(--shadow),inset 0 0 38px rgba(14,157,214,.05)}.float:before{content:"";position:absolute;inset:9px;pointer-events:none;opacity:.35;background:linear-gradient(var(--cyan),var(--cyan)) left top/28px 1px no-repeat,linear-gradient(var(--cyan),var(--cyan)) left top/1px 28px no-repeat,linear-gradient(var(--cyan),var(--cyan)) right top/28px 1px no-repeat,linear-gradient(var(--cyan),var(--cyan)) right top/1px 28px no-repeat}.panel{padding:17px 18px;min-height:145px}.panel-head{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:12px}.panel-head h3{margin:0;font-size:15px;letter-spacing:.08em;font-weight:750}.panel-head span{font-size:12px;color:var(--cyan)}.list{display:grid;gap:8px}.row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;padding:9px 10px;border:1px solid rgba(32,112,151,.30);border-radius:10px;background:rgba(3,20,33,.52);font-size:14px;line-height:1.38}.row small{display:block;color:var(--muted);font-size:12px;margin-top:2px}.row .meta{color:var(--green);font-size:12px;white-space:nowrap}.empty{padding:7px 2px;color:#7896a7;font-size:14px}
.core{min-height:720px;padding:20px 22px 18px;display:flex;flex-direction:column;align-items:center;text-align:center;background:radial-gradient(circle at 50% 35%,rgba(16,164,221,.20),transparent 27%),linear-gradient(180deg,rgba(5,23,41,.58),rgba(1,8,17,.45))}.core-title{position:relative;z-index:3;margin-bottom:2px}.core-title .eyebrow{font-size:12px;letter-spacing:.18em;color:var(--cyan)}.core-title h1{margin:5px 0 3px;font-size:30px;line-height:1.08}.core-title h1 em{font-style:normal;color:var(--cyan)}.core-title p{margin:0;color:#9bb5c5;font-size:14px}.avatar-shell{position:relative;width:min(620px,95%);height:465px;margin-top:5px;display:grid;place-items:center}.orbit,.orbit:before,.orbit:after{position:absolute;border-radius:50%;content:"";pointer-events:none}.orbit{width:410px;height:410px;border:1px solid rgba(37,220,255,.33);box-shadow:inset 0 0 56px rgba(12,181,230,.08);animation:ring 30s linear infinite}.orbit:before{inset:25px;border:1px dashed rgba(37,220,255,.24);animation:ring 18s linear infinite reverse}.orbit:after{inset:-34px;border:1px solid rgba(244,183,91,.15);animation:ring 43s linear infinite}.energy-disc{position:absolute;width:330px;height:92px;bottom:8px;border-radius:50%;background:radial-gradient(ellipse,rgba(31,221,255,.24),rgba(11,94,142,.07) 48%,transparent 70%);filter:blur(5px);animation:pulse 3s ease-in-out infinite}.avatar{position:relative;z-index:2;height:450px;max-width:100%;object-fit:contain;object-position:center bottom;filter:drop-shadow(0 0 22px rgba(28,218,255,.33)) drop-shadow(0 18px 24px rgba(0,0,0,.35));transform-origin:50% 73%;animation:breathe 5.8s ease-in-out infinite}.core[data-state="listening"] .avatar{animation:listen 1.25s ease-in-out infinite}.core[data-state="thinking"] .avatar{animation:think 2.35s ease-in-out infinite}.core[data-state="speaking"] .avatar{animation:speak .72s ease-in-out infinite}.state{position:absolute;top:9px;right:6px;z-index:4;border:1px solid rgba(45,210,255,.38);border-radius:999px;padding:6px 10px;background:rgba(4,25,41,.78);font-size:12px;color:#c9f5ff}.synth{width:min(730px,96%);margin-top:0}.synth-head{display:flex;align-items:center;justify-content:space-between;gap:10px;margin:0 5px 6px;color:#a9c5d4;font-size:13px}.synth-head b{color:#dcf8ff;font-size:14px}.scope{height:112px;border-top:1px solid rgba(40,187,235,.28);border-bottom:1px solid rgba(40,187,235,.28);background:linear-gradient(90deg,transparent,rgba(0,173,236,.07),transparent),rgba(1,10,18,.28);border-radius:10px;overflow:hidden;position:relative}.scope:before,.scope:after{content:"";position:absolute;left:7%;right:7%;height:1px;background:linear-gradient(90deg,transparent,rgba(42,228,255,.55),transparent)}.scope:before{top:22px}.scope:after{bottom:22px}.scope canvas{width:100%;height:100%;display:block;filter:drop-shadow(0 0 9px rgba(38,225,255,.7))}.voice-controls{display:flex;justify-content:center;gap:8px;flex-wrap:wrap;margin-top:10px}.voicebtn,.action{border:1px solid rgba(31,165,214,.40);border-radius:9px;background:rgba(5,28,45,.75);color:#d6f4ff;padding:9px 13px;font-size:13px;cursor:pointer}.voicebtn.active,.action.primary{border-color:#56efff;background:linear-gradient(90deg,#13bddd,#167cae);color:#00121b;font-weight:800}
.status-list{display:grid;gap:7px}.statusline{display:grid;grid-template-columns:1fr auto;gap:12px;padding-bottom:7px;border-bottom:1px solid rgba(39,98,128,.25);font-size:14px}.statusline span:last-child{color:var(--green)}.agent-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}.agent{border:1px solid rgba(35,116,151,.30);border-radius:11px;padding:10px;background:rgba(3,19,32,.53);min-height:79px;cursor:pointer;transition:.18s;text-align:left}.agent:hover{border-color:rgba(42,220,255,.6);transform:translateY(-1px)}.agent b{display:block;font-size:14px}.agent small{display:block;color:#8ca9b9;font-size:12px;margin-top:3px}.agent span{display:block;color:var(--cyan);font-size:12px;margin-top:6px}.tool-grid{display:grid;gap:7px;max-height:310px;overflow:auto;padding-right:2px}.tool{border:1px solid rgba(35,116,151,.28);border-radius:10px;padding:9px 10px;background:rgba(3,19,32,.53);cursor:pointer}.tool b{font-size:14px}.tool small{display:block;font-size:12px;color:#8ca9b9;margin-top:2px}.tool-top{display:flex;justify-content:space-between;gap:8px}.ready{color:var(--green);font-size:12px}.off{color:#738c9b;font-size:12px}.perm{display:inline-block;margin-top:5px;border-radius:999px;border:1px solid #345;padding:2px 7px;font-size:12px}.perm.green{color:var(--green);border-color:rgba(39,224,173,.35)}.perm.yellow{color:var(--gold);border-color:rgba(244,183,91,.35)}.perm.red{color:var(--red);border-color:rgba(255,100,123,.35)}
.chat{margin-top:18px;padding:18px 20px 20px;min-height:330px;background:linear-gradient(145deg,rgba(5,20,36,.75),rgba(2,10,18,.62))}.chat-head{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:12px}.chat-head h2{margin:0;font-size:17px;letter-spacing:.06em}.chat-head span{font-size:13px;color:var(--cyan)}.chatlog{height:220px;overflow:auto;display:flex;flex-direction:column;gap:10px;padding:4px 5px 12px}.bubble{max-width:min(850px,82%);padding:11px 13px;border:1px solid rgba(35,131,172,.36);border-radius:12px;background:rgba(5,27,43,.70);font-size:15px;line-height:1.55;white-space:pre-wrap;text-align:left}.bubble.user{align-self:flex-end;background:rgba(13,59,91,.76);border-color:rgba(46,174,220,.40)}.bubble strong{display:block;color:var(--cyan);font-size:12px;letter-spacing:.09em;margin-bottom:4px}.compose{display:grid;grid-template-columns:minmax(0,1fr) auto auto;gap:9px;align-items:stretch}.compose textarea{min-height:68px;max-height:150px;resize:vertical;border:1px solid rgba(54,184,225,.42);border-radius:12px;background:rgba(1,10,18,.74);color:white;padding:13px 14px;outline:none;font-size:16px;line-height:1.45}.compose button{min-width:58px;border-radius:11px;border:1px solid rgba(38,188,229,.44);background:rgba(5,31,49,.82);font-size:14px;cursor:pointer}.compose .send{min-width:100px;background:linear-gradient(90deg,#17bddd,#147aa9);border-color:#5fefff;color:#00131d;font-weight:850}.footer{display:flex;justify-content:space-between;gap:12px;padding:12px 4px 0;color:#6f8796;font-size:12px}.toast{position:fixed;right:18px;bottom:18px;z-index:100;padding:11px 14px;border:1px solid rgba(46,205,255,.4);border-radius:10px;background:#061725;color:#dcf8ff;font-size:14px;opacity:0;transform:translateY(8px);pointer-events:none;transition:.2s}.toast.show{opacity:1;transform:none}
@media(max-width:1450px){.topbar{grid-template-columns:auto 1fr}.topright{grid-column:1/-1;justify-content:flex-end;margin-top:-5px}.stage{grid-template-columns:minmax(260px,.82fr) minmax(470px,1.28fr)}.right{grid-column:1/-1;grid-template-columns:repeat(3,1fr)}}@media(max-width:1050px){.topbar{position:relative;grid-template-columns:1fr}.brandbar{min-width:0}.topcenter{grid-template-columns:1fr}.menu{order:2}.topright{grid-column:auto;justify-content:flex-start;flex-wrap:wrap}.stage{grid-template-columns:1fr}.core{order:-1}.right{grid-template-columns:1fr}.agent-grid{grid-template-columns:repeat(3,1fr)}}@media(max-width:700px){body{font-size:14px}.page{padding:10px}.topbar{padding:10px}.brandbar{flex-wrap:wrap}.sercomtec{height:28px}.menu{display:grid;grid-template-columns:repeat(3,1fr);width:100%}.menu button{padding:8px 5px}.mode-group{order:2}.engine{display:none}.core{min-height:620px;padding:16px 10px}.avatar-shell{height:390px}.avatar{height:380px}.orbit{width:320px;height:320px}.core-title h1{font-size:25px}.agent-grid{grid-template-columns:1fr 1fr}.compose{grid-template-columns:1fr auto}.compose .send{grid-column:1/-1;height:48px}.bubble{max-width:94%}}
</style>
</head>
<body>
<header class="topbar"><div class="brandbar"><div class="hakham-brand"><div class="brand-infinity">∞</div><div><b>HAKHAM INFINITY</b><small>ORBIT COMMAND // v0.7</small></div></div><div class="brand-divider"></div><img class="sercomtec" src="/assets/sercomtec-logo" alt="SER Comtec" onerror="this.style.display='none';this.nextElementSibling.style.display='inline'"><span class="ser-fallback">SER Comtec</span></div><div class="topcenter"><nav class="menu"><button class="active">COMANDO</button><button onclick="document.querySelector('#memoryPanel').scrollIntoView({behavior:'smooth'})">MEMÓRIA</button><button onclick="document.querySelector('#projectsPanel').scrollIntoView({behavior:'smooth'})">PROJETOS</button><button onclick="document.querySelector('#agentsPanel').scrollIntoView({behavior:'smooth'})">AGENTES</button><button onclick="document.querySelector('#toolsPanel').scrollIntoView({behavior:'smooth'})">TOOLS</button></nav><div class="search"><input id="globalSearch" placeholder="Buscar na memória do Hakham..."><span class="kbd">Ctrl K</span></div></div><div class="topright"><div class="mode-group"><button class="modebtn" data-mode="astra">ASTRA</button><button class="modebtn" data-mode="auto">AUTO</button><button class="modebtn" data-mode="council">CONSELHO</button></div><div class="engine" id="engineChip">carregando...</div><div class="clock"><small id="dateNow"></small><b id="timeNow"></b></div></div></header>
<main class="page"><section class="stage"><div class="stack left"><article class="float panel" id="missionsPanel"><div class="panel-head"><h3>✓ MISSÕES DO DIA</h3><span id="missionCount">0</span></div><div class="list" id="missionList"><div class="empty">Carregando missões...</div></div></article><article class="float panel" id="memoryPanel"><div class="panel-head"><h3>▣ MEMÓRIAS RECENTES</h3><span id="memoryCount">0</span></div><div class="list" id="memoryList"><div class="empty">Carregando memória...</div></div></article><article class="float panel" id="projectsPanel"><div class="panel-head"><h3>◇ PROJETOS ATIVOS</h3><span id="projectCount">0</span></div><div class="list" id="projectList"><div class="empty">Carregando projetos...</div></div></article></div><article class="float core" id="hakhamCore" data-state="idle"><div class="core-title"><div class="eyebrow">HAKHAM // CO-PILOTO ESTRATÉGICO</div><h1>Shalom, Ach. Onde vamos <em>atacar hoje?</em></h1><p>Sua visão. Minha sabedoria. Memória viva, múltiplos motores e execução coordenada.</p></div><div class="avatar-shell"><div class="orbit"></div><div class="energy-disc"></div><img class="avatar" src="/assets/hakham-official" alt="Hakham, avatar oficial"><div class="state" id="avatarState">EM ESPERA</div></div><div class="synth"><div class="synth-head"><b>VOICE REACTOR // GPT NATURAL</b><span id="voiceStatus">PRONTO</span></div><div class="scope"><canvas id="voiceScope" width="1200" height="190"></canvas></div><div class="voice-controls"><button class="voicebtn" id="listenBtn">🎙 OUVIR ACH</button><button class="voicebtn active" id="voiceToggle">🔊 VOZ GPT ATIVA</button><button class="voicebtn" id="stopVoice">■ PARAR VOZ</button></div></div></article><div class="stack right"><article class="float panel"><div class="panel-head"><h3>◉ STATUS DO SISTEMA</h3><span id="systemBadge">INICIANDO</span></div><div class="status-list" id="statusList"></div></article><article class="float panel" id="agentsPanel"><div class="panel-head"><h3>⌘ CONSELHO DE AGENTES</h3><span id="agentCount">0</span></div><div class="agent-grid" id="agentGrid"><div class="empty">Carregando agentes...</div></div></article><article class="float panel" id="toolsPanel"><div class="panel-head"><h3>⚙ TOOL GATEWAY</h3><span id="toolCount">0</span></div><div class="tool-grid" id="toolGrid"><div class="empty">Carregando ferramentas...</div></div></article></div></section><section class="float chat" id="chatPanel"><div class="chat-head"><h2>CHAT COM HAKHAM</h2><span id="chatEngine">ASTRA</span></div><div class="chatlog" id="chatLog"><div class="bubble"><strong>HAKHAM</strong>Command Deck online. Shalom, Ach. Onde vamos atacar hoje?</div></div><div class="compose"><textarea id="chatInput" placeholder="Fale ou escreva com Hakham... Enter envia · Shift+Enter quebra linha"></textarea><button id="chatMic" title="Ouvir">🎙</button><button class="send" id="sendBtn">ENVIAR</button></div></section><footer class="footer"><span>HAKHAM INFINITY ∞ v0.7 // SER Comtec</span><span>PENSE MAIS FUNDO. CONSTRUA MAIS LONGE.</span></footer></main><div class="toast" id="toast"></div>
<script>
const $=s=>document.querySelector(s);const $$=s=>Array.from(document.querySelectorAll(s));const esc=v=>String(v??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));let statusCache={},voiceEnabled=true,naturalReady=false,speechGeneration=0,naturalAudio=null,audioCtx=null,analyser=null,sourceNode=null;let recognition=null,isListening=false;
function toast(msg){const t=$('#toast');t.textContent=msg;t.classList.add('show');clearTimeout(t._x);t._x=setTimeout(()=>t.classList.remove('show'),2600)}async function jsonApi(url,options){const r=await fetch(url,options);if(!r.ok){let d=`HTTP ${r.status}`;try{d=(await r.json()).detail||d}catch(e){}throw new Error(d)}return r.json()}function setState(state,label){const c=$('#hakhamCore');c.dataset.state=state;$('#avatarState').textContent=label||({idle:'EM ESPERA',listening:'OUVINDO O ACH',thinking:'HAKHAM PENSANDO',speaking:'HAKHAM FALANDO',executing:'EXECUTANDO'}[state]||state.toUpperCase())}function tick(){const d=new Date();$('#timeNow').textContent=d.toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'});$('#dateNow').textContent=d.toLocaleDateString('pt-BR',{weekday:'short',day:'2-digit',month:'short'}).toUpperCase()}tick();setInterval(tick,1000);
function renderRows(target,items,emptyText,formatter){const el=$(target);if(!items?.length){el.innerHTML=`<div class="empty">${esc(emptyText)}</div>`;return}el.innerHTML=items.map(formatter).join('')}async function loadStatus(){try{const s=await jsonApi('/api/status');statusCache=s;naturalReady=!!s.openai_tts_ready;$('#engineChip').textContent=`${s.provider||'provider'} · ${s.model||'model'}`;$('#chatEngine').textContent=`${String(s.mode||'astra').toUpperCase()} · ${s.model||''}`;$('#systemBadge').textContent='OPERACIONAL';$('#statusList').innerHTML=[['Core',s.runtime_loaded?'CARREGADO':'STANDBY'],['Provider',s.provider||'—'],['Motor',s.model||'—'],['Memória','OK'],['Voice Loop',naturalReady?'GPT NATURAL':'FALLBACK'],['Agentes',s.agent_count??'—'],['Ferramentas',`${s.tool_configured_count??0}/${s.tool_count??0}`]].map(x=>`<div class="statusline"><span>${esc(x[0])}</span><span>${esc(x[1])}</span></div>`).join('');$$('.modebtn').forEach(b=>{b.classList.toggle('active',b.dataset.mode===s.mode);if(b.dataset.mode==='council')b.disabled=!s.council_ready});$('#voiceStatus').textContent=naturalReady?`${s.openai_tts_voice||'GPT'} · FAST`:'NAVEGADOR'}catch(e){$('#systemBadge').textContent='ERRO';toast(`Status: ${e.message}`)}}
async function loadTasks(){try{const d=await jsonApi('/api/tasks?limit=5'),items=d.items||[];$('#missionCount').textContent=items.length;renderRows('#missionList',items,'Nenhuma missão consolidada ainda.',x=>`<div class="row"><div>${esc(x.content)}<small>${esc(x.kind||'task')}</small></div><span class="meta">EM FOCO</span></div>`)}catch(e){renderRows('#missionList',[],'Missões indisponíveis.',()=> '')}}async function loadMemory(q=''){try{const url=q?`/api/memory/search?q=${encodeURIComponent(q)}&limit=6`:'/api/memory/recent?limit=6';const d=await jsonApi(url),items=d.items||[];$('#memoryCount').textContent=items.length;renderRows('#memoryList',items,q?'Nenhum resultado na memória.':'Ainda sem memórias duráveis.',x=>`<div class="row"><div>${esc(x.content)}<small>${esc(x.kind||'memória')} · ${esc(x.source||'')}</small></div><span class="meta">#${esc(x.id||'')}</span></div>`)}catch(e){renderRows('#memoryList',[],'Memória indisponível.',()=> '')}}async function loadProjects(){try{const d=await jsonApi('/api/projects?limit=5'),items=d.items||[];$('#projectCount').textContent=items.length;renderRows('#projectList',items,'Nenhum projeto consolidado na memória ainda.',x=>`<div class="row"><div>${esc(x.content)}<small>${esc(x.source||'memória semântica')}</small></div><span class="meta">ATIVO</span></div>`)}catch(e){renderRows('#projectList',[],'Projetos indisponíveis.',()=> '')}}
async function loadAgents(){try{const d=await jsonApi('/api/agents'),items=d.items||[];$('#agentCount').textContent=items.length;const g=$('#agentGrid');g.innerHTML=items.map(a=>`<button class="agent" data-agent="${esc(a.id)}"><b>${esc(a.name)}</b><small>${esc(a.description||a.specialty||a.role||'Especialista')}</small><span>DELEGAR MISSÃO</span></button>`).join('');g.querySelectorAll('[data-agent]').forEach(b=>b.onclick=()=>{const id=b.dataset.agent;if(id==='hakham'){toast('Hakham já está no comando.');return}$('#chatInput').value=`/agent ${id} `;$('#chatInput').focus();$('#chatPanel').scrollIntoView({behavior:'smooth'})})}catch(e){$('#agentGrid').innerHTML='<div class="empty">Agentes indisponíveis.</div>'}}
const toolCommands={'whatsapp.status':'/wa-status','drive.search':'/drive ','social.accounts':'/social','github.status':'/github status','github.repositories':'/github repos','cloudflare.status':'/cloudflare status','cloudflare.inventory':'/cloudflare inventory'};async function loadTools(){try{const d=await jsonApi('/api/tools'),items=d.items||[];$('#toolCount').textContent=`${d.configured||0}/${items.length}`;$('#toolGrid').innerHTML=items.map(t=>`<div class="tool" data-tool="${esc(t.id)}"><div class="tool-top"><b>${esc(t.name)}</b><span class="${t.configured?'ready':'off'}">${t.configured?'CONFIGURADA':'CONFIGURAR'}</span></div><small>${esc(t.description)}</small><span class="perm ${esc(t.permission)}">${esc(String(t.permission).toUpperCase())}</span></div>`).join('');$$('#toolGrid .tool').forEach(el=>el.onclick=()=>{const id=el.dataset.tool,cmd=toolCommands[id];if(!cmd){toast('Essa ação ainda não está exposta no chat.');return}$('#chatInput').value=cmd;$('#chatInput').focus();$('#chatPanel').scrollIntoView({behavior:'smooth'})})}catch(e){$('#toolGrid').innerHTML='<div class="empty">Tool Gateway indisponível.</div>'}}
async function setMode(mode){try{setState('thinking','TROCANDO MOTOR');const s=await jsonApi('/api/mode',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode})});statusCache={...statusCache,...s};await loadStatus();toast(`Modo ${mode.toUpperCase()} ativado`)}catch(e){toast(e.message)}finally{setState('idle')}}$$('.modebtn').forEach(b=>b.onclick=()=>setMode(b.dataset.mode));
function addBubble(role,text){const log=$('#chatLog');const d=document.createElement('div');d.className='bubble'+(role==='ACH'?' user':'');d.innerHTML=`<strong>${role}</strong>${esc(text)}`;log.appendChild(d);log.scrollTop=log.scrollHeight}async function sendChat(){const input=$('#chatInput'),text=input.value.trim();if(!text)return;input.value='';addBubble('ACH',text);setState('thinking','HAKHAM PENSANDO');try{const d=await jsonApi('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text})});addBubble('HAKHAM',d.answer);setState('idle');if(voiceEnabled)speakHakham(d.answer);loadTasks();loadMemory();loadProjects();loadStatus()}catch(e){addBubble('HAKHAM',`Falha no motor: ${e.message}`);setState('idle')}}$('#sendBtn').onclick=sendChat;$('#chatInput').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendChat()}});
function splitSpeech(text){const clean=String(text||'').replace(/\s+/g,' ').trim();if(!clean)return[];const sentences=clean.match(/[^.!?;:]+[.!?;:]+|[^.!?;:]+$/g)||[clean];const out=[];let cur='';for(const raw of sentences){const s=raw.trim(),limit=out.length?340:170,c=(cur+' '+s).trim();if(c.length<=limit)cur=c;else{if(cur)out.push(cur);cur=s}}if(cur)out.push(cur);return out}async function fetchAudio(text,generation){const r=await fetch('/api/voice/speech',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text})});if(generation!==speechGeneration)throw new Error('cancelled');if(!r.ok)throw new Error('voz GPT indisponível');return URL.createObjectURL(await r.blob())}function attachAnalyser(audio){try{audioCtx=audioCtx||new(window.AudioContext||window.webkitAudioContext)();if(sourceNode)try{sourceNode.disconnect()}catch(e){}sourceNode=audioCtx.createMediaElementSource(audio);analyser=audioCtx.createAnalyser();analyser.fftSize=512;sourceNode.connect(analyser);analyser.connect(audioCtx.destination)}catch(e){analyser=null}}async function playUrl(url,generation){if(generation!==speechGeneration){URL.revokeObjectURL(url);throw new Error('cancelled')}const a=new Audio(url);a.preload='auto';naturalAudio=a;attachAnalyser(a);await new Promise((res,rej)=>{a.onended=res;a.onerror=()=>rej(new Error('falha no áudio'));a.play().catch(rej)});URL.revokeObjectURL(url);naturalAudio=null}function browserSpeak(text){if(!('speechSynthesis'in window))return;const u=new SpeechSynthesisUtterance(text);u.lang='pt-BR';u.rate=1.05;u.pitch=.96;u.onstart=()=>setState('speaking','HAKHAM FALANDO');u.onend=()=>setState('idle');speechSynthesis.cancel();speechSynthesis.speak(u)}async function speakHakham(text){if(!voiceEnabled)return;stopSpeech();if(!naturalReady){browserSpeak(text);return}const chunks=splitSpeech(text),generation=++speechGeneration;if(!chunks.length)return;setState('speaking','HAKHAM FALANDO');try{let pending=fetchAudio(chunks[0],generation);for(let i=0;i<chunks.length;i++){const current=await pending;const next=i+1<chunks.length?fetchAudio(chunks[i+1],generation):null;await playUrl(current,generation);pending=next}if(generation===speechGeneration)setState('idle')}catch(e){if(e.message!=='cancelled'){toast('GPT Voice falhou. Usando voz do navegador.');browserSpeak(text)}}}function stopSpeech(){speechGeneration++;if(naturalAudio){try{naturalAudio.pause();naturalAudio.currentTime=0}catch(e){}naturalAudio=null}if('speechSynthesis'in window)speechSynthesis.cancel();analyser=null;setState('idle')}$('#stopVoice').onclick=stopSpeech;$('#voiceToggle').onclick=()=>{voiceEnabled=!voiceEnabled;$('#voiceToggle').classList.toggle('active',voiceEnabled);$('#voiceToggle').textContent=voiceEnabled?'🔊 VOZ GPT ATIVA':'🔇 VOZ DESLIGADA';if(!voiceEnabled)stopSpeech()};
function initRecognition(){const SR=window.SpeechRecognition||window.webkitSpeechRecognition;if(!SR)return null;const r=new SR();r.lang='pt-BR';r.interimResults=false;r.continuous=false;r.onstart=()=>{isListening=true;setState('listening','OUVINDO O ACH');$('#listenBtn').classList.add('active')};r.onresult=e=>{const text=Array.from(e.results).map(x=>x[0].transcript).join(' ').trim();if(text){$('#chatInput').value=text;sendChat()}};r.onerror=e=>{toast(`Microfone: ${e.error||'erro'}`);setState('idle')};r.onend=()=>{isListening=false;$('#listenBtn').classList.remove('active');if($('#hakhamCore').dataset.state==='listening')setState('idle')};return r}recognition=initRecognition();function toggleListen(){if(!recognition){toast('Reconhecimento de voz não disponível neste navegador.');return}if(isListening)recognition.stop();else recognition.start()}$('#listenBtn').onclick=toggleListen;$('#chatMic').onclick=toggleListen;
const scope=$('#voiceScope'),ctx=scope.getContext('2d');function drawScope(){const w=scope.width,h=scope.height;ctx.clearRect(0,0,w,h);const state=$('#hakhamCore').dataset.state;let data=null;if(analyser){data=new Uint8Array(analyser.frequencyBinCount);analyser.getByteFrequencyData(data)}const t=Date.now()/1000;ctx.lineWidth=2.3;ctx.strokeStyle=state==='listening'?'#27e0ad':'#25dcff';ctx.beginPath();for(let x=0;x<w;x+=4){const env=Math.sin(Math.PI*x/w),idx=data?Math.floor((x/w)*data.length):0,raw=data?data[idx]/255:((state==='speaking'||state==='listening')?.23+.13*Math.sin(t*10+x*.045):.045+.02*Math.sin(t*2+x*.025));const amp=raw*78*env;const y=h/2+Math.sin(x*.16+t*7)*amp;ctx.lineTo(x,y)}ctx.stroke();ctx.strokeStyle='rgba(244,183,91,.42)';ctx.lineWidth=1.3;ctx.beginPath();for(let x=0;x<w;x+=7){ctx.lineTo(x,h/2+Math.sin(t*3+x*.025)*9*Math.sin(Math.PI*x/w))}ctx.stroke();requestAnimationFrame(drawScope)}drawScope();
$('#globalSearch').addEventListener('keydown',e=>{if(e.key==='Enter'){loadMemory(e.target.value.trim());$('#memoryPanel').scrollIntoView({behavior:'smooth'})}});document.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();$('#globalSearch').focus()}});Promise.allSettled([loadStatus(),loadTasks(),loadMemory(),loadProjects(),loadAgents(),loadTools()]);
</script></body></html>"""
