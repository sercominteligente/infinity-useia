from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse, Response

from . import web as backend
from . import web_v5 as previous
from .command_router import CommandRouter


app = FastAPI(title="HAKHAM Infinity Control Center", version="0.6.0")


def _reference_file() -> Path:
    return Path("assets/hakham-reference.webp")


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return CONTROL_CENTER_HTML


@app.get("/assets/hakham-reference")
def avatar_reference() -> FileResponse:
    path = _reference_file()
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Hakham reference art is not installed")
    return FileResponse(path, media_type="image/webp", headers={"Cache-Control": "no-cache"})


@app.get("/assets/hakham-avatar")
def avatar_asset() -> FileResponse:
    return previous.avatar_asset()


@app.get("/api/status")
def status() -> dict[str, object]:
    payload = previous.status()
    reference_ready = _reference_file().is_file()
    payload.update(
        {
            "version": "0.6.0",
            "avatar_reference_ready": reference_ready,
            "avatar_reference_url": "/assets/hakham-reference" if reference_ready else "",
            "ui_generation": "cockpit-v2",
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
def speech(request: previous.previous.SpeechRequest) -> Response:
    return previous.speech(request)


@app.get("/api/agents")
def list_agents() -> dict[str, object]:
    return previous.list_agents()


@app.post("/api/agents/delegate")
def delegate_agent(request: previous.AgentTaskRequest) -> dict[str, object]:
    return previous.delegate_agent(request)


@app.get("/api/tools")
def list_tools() -> dict[str, object]:
    return previous.list_tools()


@app.post("/api/tools/execute")
def execute_tool(request: previous.ToolExecuteRequest) -> dict[str, object]:
    return previous.execute_tool(request)


def main() -> None:
    import uvicorn

    uvicorn.run("hakham.web_v6:app", host="127.0.0.1", port=8765, reload=False)


CONTROL_CENTER_HTML = r'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>HAKHAM Infinity // Command Deck</title>
<style>
:root{color-scheme:dark;--bg:#01050b;--bg2:#03111d;--glass:#061725d9;--glass2:#081c2bd9;--line:#14577d;--line2:#0a3450;--cyan:#16e0ff;--cyan2:#7af5ff;--blue:#1c88ff;--gold:#ffb74a;--green:#18e5aa;--red:#ff5f77;--text:#ecf9ff;--muted:#7d9cae;--violet:#865cff}
*{box-sizing:border-box}html{background:var(--bg)}body{margin:0;min-height:100vh;overflow-x:hidden;color:var(--text);font-family:Inter,Segoe UI,Arial,sans-serif;background:radial-gradient(circle at 63% 0,#0a3558 0,#03111d 26%,#01050b 62%)}button,input,textarea{font:inherit}.app{min-height:100vh;display:grid;grid-template-columns:86px minmax(0,1fr)}
.rail{position:sticky;top:0;height:100vh;z-index:30;display:flex;flex-direction:column;align-items:center;padding:16px 10px;background:linear-gradient(180deg,#020b14fa,#01060cf5);border-right:1px solid #0c3e60;box-shadow:12px 0 42px #000a}.logo{font-weight:900;font-size:21px;line-height:.9;letter-spacing:.11em;text-align:center;margin:4px 0 22px}.logo span{display:block;color:var(--cyan);font-size:10px;margin-top:8px}.infinity{font-size:31px;color:var(--cyan);text-shadow:0 0 22px #13dfff}.railnav{display:grid;gap:11px;width:100%}.navbtn{height:58px;border:1px solid transparent;border-radius:14px;background:transparent;color:#6f9aaf;cursor:pointer;display:grid;place-items:center;gap:2px;font-size:9px}.navbtn b{font-size:20px;font-weight:500}.navbtn:hover,.navbtn.active{color:white;border-color:#13618e;background:linear-gradient(180deg,#0a2940,#061725);box-shadow:0 0 24px #0c83bd3d inset}.ach-mini{margin-top:auto;width:64px;padding:8px 4px;border:1px solid #15587e;border-radius:14px;background:#071725;text-align:center}.ach-mini .wolf{font-size:25px}.ach-mini small{display:block;color:var(--green);font-size:8px}.ach-mini b{font-size:10px}
.deck{min-width:0;padding:12px 16px 112px}.topbar{height:58px;display:grid;grid-template-columns:minmax(260px,1fr) minmax(360px,680px) minmax(260px,1fr);align-items:center;gap:15px;border-bottom:1px solid #0a3450;margin-bottom:12px}.deck-title{font-size:11px;letter-spacing:.22em;color:#77a9c2}.searchbox{position:relative}.searchbox input{width:100%;height:40px;border:1px solid #155178;border-radius:12px;background:#061522;color:white;padding:0 48px 0 42px;outline:none;box-shadow:0 0 22px #0494cc14 inset}.searchbox:before{content:'⌕';position:absolute;left:14px;top:7px;color:#88c8e7;font-size:22px}.kbd{position:absolute;right:9px;top:10px;padding:3px 6px;border:1px solid #1b5275;border-radius:5px;color:#6e9aae;font-size:9px}.topmeta{display:flex;justify-content:flex-end;align-items:center;gap:10px}.time{text-align:right;line-height:1.05}.time small{display:block;color:#79a0b6;font-size:9px}.time b{font-size:20px}.engine-pill{border:1px solid #12618e;border-radius:999px;padding:7px 11px;background:#061828;font-size:10px;color:#aeeeff;white-space:nowrap}
.command-grid{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(460px,.95fr) 330px;gap:12px;min-height:500px}.glass{position:relative;border:1px solid #10537a;border-radius:16px;background:linear-gradient(180deg,#071826e8,#03101be8);box-shadow:0 18px 52px #0009,0 0 45px #0c8ac21a inset;overflow:hidden}.glass:before{content:'';position:absolute;inset:9px;pointer-events:none;background:linear-gradient(var(--cyan),var(--cyan)) left top/30px 1px no-repeat,linear-gradient(var(--cyan),var(--cyan)) left top/1px 30px no-repeat,linear-gradient(var(--cyan),var(--cyan)) right top/30px 1px no-repeat,linear-gradient(var(--cyan),var(--cyan)) right top/1px 30px no-repeat;opacity:.32}.mission{padding:26px 26px 20px;display:flex;flex-direction:column;min-height:500px}.eyebrow{font-size:10px;letter-spacing:.19em;color:var(--cyan)}.mission h1{font-size:clamp(36px,4.4vw,68px);line-height:.96;margin:12px 0 11px;max-width:690px}.mission h1 em{font-style:normal;color:var(--cyan);text-shadow:0 0 22px #16e0ff55}.mission p{max-width:570px;color:#8facbd;line-height:1.55;margin:0 0 20px}.mission-actions{display:flex;gap:9px;flex-wrap:wrap}.primary,.ghost,.modebtn,.iconbtn{cursor:pointer;border-radius:10px}.primary{padding:11px 16px;border:1px solid #4cf0ff;background:linear-gradient(90deg,#13c6e8,#1684bc);color:#021018;font-weight:800;box-shadow:0 0 26px #12dfff3d}.ghost{padding:11px 15px;border:1px solid #185d83;background:#071927;color:#c6ecff}.voice-panel{margin-top:auto;display:grid;grid-template-columns:1fr auto;gap:12px;align-items:end;padding-top:22px}.voice-copy small{display:block;color:#6c9bb2;font-size:9px;letter-spacing:.13em}.voice-copy b{display:block;font-size:13px;margin-top:4px}.voice-actions{display:flex;gap:7px;flex-wrap:wrap;justify-content:flex-end}.iconbtn{border:1px solid #16618b;background:#071d2c;color:#c6efff;padding:9px 11px;font-size:11px}.iconbtn.active{border-color:#38e8ff;background:#0c5875;color:#fff;box-shadow:0 0 22px #20dfff3a}.voice-line{height:80px;margin-top:10px;border-top:1px solid #0e405f;border-bottom:1px solid #0e405f;background:linear-gradient(90deg,transparent,#0a55752b,transparent);position:relative}.voice-line canvas{width:100%;height:100%;display:block;filter:drop-shadow(0 0 10px #1ee8ff88)}
.avatar-stage{min-height:500px;display:grid;place-items:center;position:relative;background:radial-gradient(circle at 50% 45%,#0f4d7050,transparent 35%),linear-gradient(180deg,#061725,#020914)}.avatar-stage .rings{position:absolute;width:420px;height:420px;border-radius:50%;border:1px solid #18d9ff62;box-shadow:0 0 42px #0ec9ff2d inset;animation:spin 22s linear infinite}.avatar-stage .rings:before,.avatar-stage .rings:after{content:'';position:absolute;border-radius:50%;border:1px dashed #15cfff55;inset:24px;animation:spin 14s linear infinite reverse}.avatar-stage .rings:after{inset:-31px;border-color:#ffb74a42;animation-duration:31s}.avatar-crop{position:relative;width:min(470px,94%);height:455px;overflow:hidden;z-index:2;filter:drop-shadow(0 0 22px #15dfff50);transform-origin:50% 75%;animation:breathe 5.7s ease-in-out infinite}.avatar-crop img.reference{position:absolute;width:1290px;max-width:none;left:50%;top:-52px;transform:translateX(-50%);user-select:none;pointer-events:none}.avatar-crop img.transparent{position:absolute;width:96%;height:96%;object-fit:contain;left:2%;top:2%;user-select:none;pointer-events:none}.avatar-stage.listening .avatar-crop{animation:listen 1.2s ease-in-out infinite}.avatar-stage.thinking .avatar-crop{animation:think 2.4s ease-in-out infinite}.avatar-stage.speaking .avatar-crop{animation:speak .7s ease-in-out infinite}.avatar-stage.executing .avatar-crop{animation:execute .9s ease-in-out infinite}.avatar-tag{position:absolute;left:18px;top:17px;z-index:5;font-size:10px;color:var(--cyan);letter-spacing:.14em}.avatar-state{position:absolute;right:18px;top:16px;z-index:5;border:1px solid #16628b;border-radius:999px;padding:6px 10px;font-size:9px;color:#c9f4ff;background:#061827cc}.avatar-glow{position:absolute;bottom:28px;left:50%;transform:translateX(-50%);z-index:6;font-size:54px;color:white;text-shadow:0 0 16px #1de8ff,0 0 45px #0a9fdc}.mouth-pulse{position:absolute;z-index:7;left:50%;top:47%;width:44px;height:7px;border-radius:999px;background:#24e8ff;box-shadow:0 0 25px #1eeaff;opacity:0;transform:translate(-50%,-50%)}.avatar-stage.speaking .mouth-pulse{opacity:.55;animation:mouth .16s ease-in-out infinite alternate}
.syscol{display:grid;grid-template-rows:auto 1fr auto;gap:12px}.system{padding:18px}.cardtitle{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:13px;font-size:11px;letter-spacing:.12em}.status-badge{font-size:9px;color:var(--green);border:1px solid #178e6b;border-radius:999px;padding:4px 7px}.status-list{display:grid;gap:8px}.status-row{display:grid;grid-template-columns:1fr auto;gap:10px;padding-bottom:7px;border-bottom:1px solid #0b314b;font-size:11px}.status-row span:last-child{color:var(--green)}.modebox{padding:17px}.modes{display:grid;grid-template-columns:repeat(3,1fr);gap:7px}.modebtn{border:1px solid #174d6e;background:#061623;color:#7ca5b9;padding:9px 7px;font-size:9px}.modebtn.active{color:#03131b;background:var(--cyan);border-color:#6ff4ff;font-weight:900}.modebtn:disabled{opacity:.38;cursor:not-allowed}.ach-card{padding:18px}.ach-row{display:flex;gap:12px;align-items:center}.wolf-big{width:62px;height:62px;border-radius:17px;border:1px solid #196389;display:grid;place-items:center;font-size:38px;background:radial-gradient(circle,#13364c,#05111d)}.ach-card h3{margin:0;font-size:16px}.ach-card p{margin:4px 0 0;color:#7fa5b9;font-size:10px}.quote2{margin-top:14px;border-left:2px solid var(--gold);padding-left:10px;font-size:11px;line-height:1.5;color:#bbd2df}
.data-grid{display:grid;grid-template-columns:1.05fr 1fr 1fr;gap:12px;margin-top:12px}.data-card{min-height:235px;padding:17px}.list{display:grid;gap:8px}.item{padding:9px 10px;border:1px solid #0d3c58;border-radius:9px;background:#051521;display:grid;grid-template-columns:1fr auto;gap:8px;font-size:11px}.item small{display:block;color:#6f98ad;font-size:9px;margin-top:2px}.item .dot{width:7px;height:7px;border-radius:50%;background:var(--green);box-shadow:0 0 10px #18e5aa;margin-top:4px}.empty{color:#607f90;font-size:11px;padding:8px 0}.agent-strip{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:8px}.agent{border:1px solid #0e405d;border-radius:11px;padding:10px;background:#051521;cursor:pointer;min-height:86px;transition:.2s}.agent:hover{border-color:#19b7e8;transform:translateY(-1px);box-shadow:0 0 20px #12cfff17}.agent b{font-size:11px}.agent small{display:block;color:#6f95aa;font-size:9px;margin-top:5px}.agent .role{margin-top:8px;color:var(--cyan);font-size:8px}.tool-list{display:grid;gap:7px}.tool{padding:9px;border:1px solid #0f405c;border-radius:9px;background:#051521;font-size:10px}.tool .tstate{float:right;font-size:8px}.tool .tstate.on{color:var(--green)}.tool .tstate.off{color:#6e8796}.perm{display:inline-block;margin-top:5px;border-radius:999px;padding:2px 6px;border:1px solid #345;font-size:8px}.perm.green{color:var(--green);border-color:#1b765c}.perm.yellow{color:var(--gold);border-color:#7d5b25}.perm.red{color:var(--red);border-color:#7b2c39}
.chatdock{position:fixed;z-index:40;left:102px;right:16px;bottom:12px;border:1px solid #17638e;border-radius:16px;background:linear-gradient(180deg,#061827f5,#020b13f7);box-shadow:0 -18px 65px #000b,0 0 35px #0e9ad11b inset;padding:10px}.chatlog{max-height:175px;overflow:auto;display:grid;gap:7px;margin-bottom:8px}.bubble{max-width:78%;padding:9px 11px;border-radius:10px;border:1px solid #155171;background:#071b29;font-size:11px;line-height:1.45;white-space:pre-wrap}.bubble.user{justify-self:end;background:#0d3554;border-color:#1a6994}.bubble strong{display:block;color:var(--cyan);font-size:8px;letter-spacing:.12em;margin-bottom:4px}.chatrow{display:grid;grid-template-columns:1fr auto auto;gap:8px}.chatrow textarea{resize:none;height:44px;border:1px solid #1a638e;border-radius:10px;background:#020c14;color:white;padding:12px;outline:none}.send{border:1px solid #48e8ff;border-radius:10px;background:linear-gradient(90deg,#12bddd,#137cb0);color:#021018;font-weight:900;padding:0 16px;cursor:pointer}.mic{width:46px;border:1px solid #17658f;border-radius:10px;background:#071d2b;color:#bfeeff;cursor:pointer}.toast{position:fixed;right:18px;bottom:100px;z-index:99;border:1px solid #1b729a;background:#061725;padding:10px 13px;border-radius:10px;color:#c9f5ff;font-size:11px;opacity:0;transform:translateY(8px);pointer-events:none;transition:.2s}.toast.show{opacity:1;transform:none}
@keyframes spin{to{transform:rotate(360deg)}}@keyframes breathe{0%,100%{transform:translateY(3px) scale(1)}50%{transform:translateY(-3px) scale(1.012)}}@keyframes listen{0%,100%{transform:scale(1.01) rotate(-.3deg)}50%{transform:scale(1.027) rotate(.5deg)}}@keyframes think{0%,100%{transform:translateY(1px)}50%{transform:translateY(-6px) rotate(.4deg)}}@keyframes speak{0%,100%{transform:translateY(1px) scale(1.012)}50%{transform:translateY(-3px) scale(1.026)}}@keyframes execute{0%,100%{filter:drop-shadow(0 0 22px #15dfff50)}50%{filter:drop-shadow(0 0 44px #ffb74a88);transform:scale(1.025)}}@keyframes mouth{from{transform:translate(-50%,-50%) scaleX(.4)}to{transform:translate(-50%,-50%) scaleX(1.25)}}
@media(max-width:1350px){.command-grid{grid-template-columns:1fr 470px}.syscol{grid-column:1/-1;grid-template-columns:1fr 1fr 1fr;grid-template-rows:auto}.data-grid{grid-template-columns:1fr 1fr}.data-card.agents-card{grid-column:1/-1}.topbar{grid-template-columns:1fr minmax(340px,600px) auto}}@media(max-width:900px){.app{grid-template-columns:1fr}.rail{display:none}.deck{padding:8px 8px 120px}.topbar{grid-template-columns:1fr auto}.searchbox{grid-column:1/-1;grid-row:2}.command-grid{grid-template-columns:1fr}.avatar-stage{min-height:440px}.syscol{grid-template-columns:1fr}.data-grid{grid-template-columns:1fr}.agent-strip{grid-template-columns:repeat(2,1fr)}.chatdock{left:8px;right:8px}.mission h1{font-size:42px}.avatar-crop{width:100%;height:410px}.avatar-crop img.reference{width:1180px;top:-48px}}
</style>
</head>
<body>
<div class="app">
  <aside class="rail"><div class="logo">HAKHAM<span>INFINITY</span><div class="infinity">∞</div></div><nav class="railnav"><button class="navbtn active"><b>⌂</b><span>HOME</span></button><button class="navbtn"><b>▣</b><span>MEMÓRIA</span></button><button class="navbtn"><b>◇</b><span>PROJETOS</span></button><button class="navbtn"><b>⌘</b><span>AGENTES</span></button><button class="navbtn"><b>⚙</b><span>TOOLS</span></button><button class="navbtn"><b>◉</b><span>CONFIG</span></button></nav><div class="ach-mini"><div class="wolf">🐺</div><small>● ONLINE</small><b>ACH</b></div></aside>
  <main class="deck"><header class="topbar"><div class="deck-title">HAKHAM // COMMAND DECK</div><div class="searchbox"><input id="globalSearch" placeholder="Buscar memórias, projetos, arquivos, comandos..."><span class="kbd">Ctrl K</span></div><div class="topmeta"><div class="time"><small id="dateLabel">SISTEMA LOCAL</small><b id="clock">--:--</b></div><span class="engine-pill" id="enginePill">carregando motor...</span></div></header>
    <section class="command-grid"><article class="glass mission"><div class="eyebrow">∞ HAKHAM // COPILOTO ESTRATÉGICO</div><h1>Eaew Ach,<br>onde vamos <em>atacar hoje?</em></h1><p>Sua visão. Minha sabedoria. Memória viva, agentes especializados e ferramentas reais sob um único centro de comando.</p><div class="mission-actions"><button class="primary" id="focusChat">▶ CONVERSAR COM HAKHAM</button><button class="ghost" id="planNow">⌁ PLANEJAR AGORA</button><button class="ghost" id="showHelp">⌘ COMANDOS</button></div><div class="voice-panel"><div class="voice-copy"><small>VOICE REACTOR // GPT NATURAL</small><b id="voiceStatus">Preparando sintetizador...</b></div><div class="voice-actions"><button class="iconbtn" id="micTop">🎙 OUVIR</button><button class="iconbtn active" id="voiceToggle">🔊 VOZ ON</button><button class="iconbtn" id="stopVoice">■ PARAR</button></div></div><div class="voice-line"><canvas id="voiceCanvas" width="1200" height="160"></canvas></div></article>
      <article class="glass avatar-stage" id="avatarStage"><div class="avatar-tag">HAKHAM // AVATAR OFICIAL</div><div class="avatar-state" id="avatarState">EM ESPERA</div><div class="rings"></div><div class="avatar-crop" id="avatarCrop"><div class="empty" id="avatarFallback">Carregando o velho da lancha... 😂</div><img id="avatarImg" alt="Hakham"></div><div class="mouth-pulse"></div><div class="avatar-glow">∞</div></article>
      <aside class="syscol"><article class="glass system"><div class="cardtitle"><span>⚙ STATUS DO SISTEMA</span><span class="status-badge">OPERACIONAL</span></div><div class="status-list" id="systemList"><div class="empty">Consultando núcleo...</div></div></article><article class="glass modebox"><div class="cardtitle"><span>◈ MOTOR DE PROPULSÃO</span><span id="modeLabel">ASTRA</span></div><div class="modes"><button class="modebtn" data-mode="astra">ASTRA</button><button class="modebtn" data-mode="auto">AUTO</button><button class="modebtn" data-mode="council">CONSELHO</button></div></article><article class="glass ach-card"><div class="ach-row"><div class="wolf-big">🐺</div><div><h3>ACH</h3><p>Comandante do Lobo // Modo Estratégico</p></div></div><div class="quote2">“DISCIPLINA. EXECUÇÃO. RESULTADOS. SEMPRE.”</div></article></aside></section>
    <section class="data-grid"><article class="glass data-card"><div class="cardtitle"><span>✓ MISSÕES DO DIA</span><span id="taskCount">0 em foco</span></div><div class="list" id="tasksList"><div class="empty">Buscando missões...</div></div></article><article class="glass data-card"><div class="cardtitle"><span>◇ PROJETOS ATIVOS</span><span>memória semântica</span></div><div class="list" id="projectsList"><div class="empty">Buscando projetos...</div></div></article><article class="glass data-card"><div class="cardtitle"><span>▣ MEMÓRIAS RECENTES</span><span id="memoryCount">0</span></div><div class="list" id="memoryList"><div class="empty">Buscando memórias...</div></div></article><article class="glass data-card agents-card"><div class="cardtitle"><span>⌘ CONSELHO DE AGENTES</span><span id="agentCount">0 online</span></div><div class="agent-strip" id="agentStrip"><div class="empty">Chamando a equipe...</div></div></article><article class="glass data-card"><div class="cardtitle"><span>⚙ TOOL GATEWAY</span><span id="toolCount">0/0</span></div><div class="tool-list" id="toolList"><div class="empty">Mapeando ferramentas...</div></div></article><article class="glass data-card"><div class="cardtitle"><span>✦ SUGESTÕES DO HAKHAM</span><span>próximo ataque</span></div><div class="list" id="suggestions"><div class="item"><div>1. Configurar WhatsApp e Drive no Tool Gateway<small>Integração</small></div><span>›</span></div><div class="item"><div>2. Ativar 2 ou 3 motores no Conselho<small>Inteligência</small></div><span>›</span></div><div class="item"><div>3. Delegar primeira missão ao Serafim<small>Agentes</small></div><span>›</span></div></div></article></section></main>
</div>
<section class="chatdock"><div class="chatlog" id="chatLog"><div class="bubble"><strong>HAKHAM</strong>Command Deck v0.6 online. Shalom, Ach. Onde vamos atacar hoje?</div></div><div class="chatrow"><textarea id="chatInput" placeholder="Fale ou escreva com Hakham... /help mostra comandos"></textarea><button class="mic" id="micDock">🎙</button><button class="send" id="sendBtn">ENVIAR</button></div></section><div class="toast" id="toast"></div>
<script>
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
let systemStatus=null, voiceEnabled=true, speaking=false, speechGeneration=0, currentAudio=null, audioContext=null, analyser=null, sourceNode=null, recognition=null;
function toast(msg){const el=$('#toast');el.textContent=msg;el.classList.add('show');clearTimeout(window.__toast);window.__toast=setTimeout(()=>el.classList.remove('show'),2600)}
function setState(state,label){const stage=$('#avatarStage');stage.classList.remove('listening','thinking','speaking','executing');if(state!=='idle')stage.classList.add(state);$('#avatarState').textContent=label||state.toUpperCase()}
function addMsg(author,text,user=false){const b=document.createElement('div');b.className='bubble'+(user?' user':'');b.innerHTML=`<strong>${esc(author)}</strong>${esc(text)}`;$('#chatLog').appendChild(b);$('#chatLog').scrollTop=$('#chatLog').scrollHeight}
function clockTick(){const d=new Date();$('#clock').textContent=d.toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'});$('#dateLabel').textContent=d.toLocaleDateString('pt-BR',{weekday:'short',day:'2-digit',month:'short',year:'numeric'}).toUpperCase()}clockTick();setInterval(clockTick,1000);
function drawVoice(){const c=$('#voiceCanvas'),ctx=c.getContext('2d'),w=c.width,h=c.height;ctx.clearRect(0,0,w,h);let data=null;if(analyser){data=new Uint8Array(analyser.frequencyBinCount);analyser.getByteFrequencyData(data)}const active=speaking||$('#avatarStage').classList.contains('listening');ctx.lineWidth=2;ctx.strokeStyle=$('#avatarStage').classList.contains('listening')?'#18e5aa':'#16e0ff';ctx.beginPath();for(let x=0;x<w;x+=5){const i=data?Math.floor(x/w*data.length):0;const base=data?data[i]/255:(active?.2+.12*Math.sin(Date.now()/115+x*.045):.035);const env=Math.sin(Math.PI*x/w);const amp=base*66*env;const y=h/2+(x%10===0?1:-1)*amp;if(x===0)ctx.moveTo(x,y);else ctx.lineTo(x,y)}ctx.stroke();ctx.strokeStyle='rgba(255,183,74,.42)';ctx.beginPath();for(let x=0;x<w;x+=11){const y=h/2+Math.sin(Date.now()/260+x*.031)*7;if(x===0)ctx.moveTo(x,y);else ctx.lineTo(x,y)}ctx.stroke();requestAnimationFrame(drawVoice)}drawVoice();
function attachAnalyser(audio){try{audioContext=audioContext||new(window.AudioContext||window.webkitAudioContext)();if(audioContext.state==='suspended')audioContext.resume();analyser=audioContext.createAnalyser();analyser.fftSize=256;sourceNode=audioContext.createMediaElementSource(audio);sourceNode.connect(analyser);analyser.connect(audioContext.destination)}catch(e){analyser=null}}
function cleanSpeech(text){return String(text||'').replace(/\b[kK](?:\s*[kK]){2,}\b/g,'haha').replace(/\s+/g,' ').trim()}
function chunks(text){const clean=cleanSpeech(text);const s=clean.match(/[^.!?;:]+[.!?;:]+|[^.!?;:]+$/g)||[clean];const out=[];let cur='';for(const raw of s){const sentence=raw.trim();if(!sentence)continue;const limit=out.length?360:170;const candidate=(cur+' '+sentence).trim();if(candidate.length<=limit)cur=candidate;else{if(cur)out.push(cur);cur=sentence}}if(cur)out.push(cur);return out}
async function fetchSpeech(text,generation){const r=await fetch('/api/voice/speech',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text})});if(generation!==speechGeneration)throw new Error('cancelled');if(!r.ok)throw new Error((await r.json()).detail||'voz indisponível');return URL.createObjectURL(await r.blob())}
async function playUrl(url,generation){if(generation!==speechGeneration){URL.revokeObjectURL(url);return}const a=new Audio(url);currentAudio=a;attachAnalyser(a);await new Promise((resolve,reject)=>{a.onended=resolve;a.onerror=()=>reject(new Error('erro no áudio'));a.play().catch(reject)});URL.revokeObjectURL(url);currentAudio=null;analyser=null;sourceNode=null}
async function speak(text){if(!voiceEnabled||!text)return;stopVoice(false);const parts=chunks(text);if(!parts.length)return;const gen=++speechGeneration;speaking=true;setState('speaking','HAKHAM FALANDO');$('#voiceStatus').textContent='GPT Voice em streaming por blocos';try{let pending=fetchSpeech(parts[0],gen);for(let i=0;i<parts.length;i++){const url=await pending;const next=i+1<parts.length?fetchSpeech(parts[i+1],gen):null;await playUrl(url,gen);pending=next}}catch(e){if(e.message!=='cancelled'){toast('GPT Voice falhou. Usando voz do navegador.');browserSpeak(text)}}finally{if(gen===speechGeneration){speaking=false;setState('idle','EM ESPERA')}}}
function browserSpeak(text){if(!('speechSynthesis'in window))return;const u=new SpeechSynthesisUtterance(cleanSpeech(text));u.lang='pt-BR';u.rate=1.08;u.pitch=.96;u.onstart=()=>{speaking=true;setState('speaking','HAKHAM FALANDO')};u.onend=()=>{speaking=false;setState('idle','EM ESPERA')};speechSynthesis.speak(u)}
function stopVoice(increment=true){if(increment)speechGeneration++;if(currentAudio){try{currentAudio.pause();currentAudio.currentTime=0}catch(e){}currentAudio=null}if('speechSynthesis'in window)speechSynthesis.cancel();speaking=false;analyser=null;setState('idle','EM ESPERA')}
async function loadStatus(){const r=await fetch('/api/status'),s=await r.json();systemStatus=s;$('#enginePill').textContent=`${s.provider||'?'} · ${s.model||'?'}`;$('#modeLabel').textContent=String(s.mode||'custom').toUpperCase();$$('.modebtn').forEach(b=>{b.classList.toggle('active',b.dataset.mode===s.mode);if(b.dataset.mode==='council')b.disabled=!s.council_ready});$('#systemList').innerHTML=[['Core',s.runtime_loaded?'CARREGADO':'STANDBY'],['Provider',s.provider],['Motor',s.model],['Memória','OK'],['Voice Loop',s.openai_tts_ready?'PRONTO':'FALLBACK'],['Agentes',String(s.agent_count||0)],['Ferramentas',`${s.tool_configured_count||0}/${s.tool_count||0}`]].map(x=>`<div class="status-row"><span>${esc(x[0])}</span><span>${esc(x[1])}</span></div>`).join('');const img=$('#avatarImg'),fallback=$('#avatarFallback');if(s.avatar_url){img.className='transparent';img.src=s.avatar_url;img.onload=()=>fallback.style.display='none'}else if(s.avatar_reference_url){img.className='reference';img.src=s.avatar_reference_url;img.onload=()=>fallback.style.display='none'}else{fallback.textContent='Falta instalar o velho da lancha em assets/'};$('#voiceStatus').textContent=s.openai_tts_ready?`GPT Natural · ${s.openai_tts_voice||'voice'} · FAST`:'Voz do navegador · fallback';}
async function loadList(url,el,kind){try{const r=await fetch(url),d=await r.json(),items=d.items||[];if(kind==='tasks')$('#taskCount').textContent=`${items.length} em foco`;if(kind==='memory')$('#memoryCount').textContent=items.length;if(!items.length){$(el).innerHTML='<div class="empty">Ainda sem dados consolidados neste ambiente.</div>';return}$(el).innerHTML=items.map(i=>`<div class="item"><div>${esc(i.content||i.name||'item')}<small>${esc(i.kind||i.source||kind)}</small></div><span class="dot"></span></div>`).join('')}catch(e){$(el).innerHTML='<div class="empty">Indisponível.</div>'}}
async function loadAgents(){try{const r=await fetch('/api/agents'),d=await r.json(),items=d.items||[];$('#agentCount').textContent=`${items.length} online`;$('#agentStrip').innerHTML=items.map(a=>`<div class="agent" data-id="${esc(a.id)}" data-role="${esc(a.role)}"><b>${esc(a.icon)} ${esc(a.name)}</b><small>${esc(a.specialty)}</small><div class="role">${a.role==='orchestrator'?'ORQUESTRADOR':'DELEGAR MISSÃO'}</div></div>`).join('');$$('.agent[data-role="specialist"]').forEach(el=>el.onclick=()=>delegateAgent(el.dataset.id,el.querySelector('b').textContent))}catch(e){$('#agentStrip').innerHTML='<div class="empty">Agentes indisponíveis.</div>'}}
async function loadTools(){try{const r=await fetch('/api/tools'),d=await r.json(),items=d.items||[];$('#toolCount').textContent=`${d.configured||0}/${items.length} configuradas`;$('#toolList').innerHTML=items.slice(0,5).map(t=>`<div class="tool"><span class="tstate ${t.configured?'on':'off'}">${t.configured?'CONFIGURADA':'CONFIGURAR'}</span><b>${esc(t.name)}</b><div>${esc(t.description)}</div><span class="perm ${esc(t.permission)}">${String(t.permission).toUpperCase()}</span></div>`).join('')}catch(e){$('#toolList').innerHTML='<div class="empty">Gateway indisponível.</div>'}}
async function delegateAgent(id,name){const task=prompt(`Missão para ${name}:`);if(!task)return;setState('executing','DELEGANDO MISSÃO');toast(`${name} entrou em missão...`);try{const r=await fetch('/api/agents/delegate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({agent_id:id,message:task})}),d=await r.json();if(!r.ok)throw new Error(d.detail||'falha');addMsg(d.name,d.answer);if(voiceEnabled)speak(d.answer)}catch(e){toast(e.message)}finally{setState('idle','EM ESPERA')}}
async function sendChat(){const input=$('#chatInput'),msg=input.value.trim();if(!msg)return;input.value='';addMsg('ACH',msg,true);setState('thinking','HAKHAM PENSANDO');$('#sendBtn').disabled=true;try{const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})}),d=await r.json();if(!r.ok)throw new Error(d.detail||'falha no núcleo');addMsg('HAKHAM',d.answer);if(voiceEnabled)speak(d.answer);await loadStatus();loadList('/api/memory/recent?limit=5','#memoryList','memory')}catch(e){addMsg('SISTEMA',e.message);toast(e.message)}finally{$('#sendBtn').disabled=false;if(!speaking)setState('idle','EM ESPERA')}}
async function setMode(mode){try{const r=await fetch('/api/mode',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode})}),d=await r.json();if(!r.ok)throw new Error(d.detail||'falha');toast(`Modo ${mode.toUpperCase()} ativado`);loadStatus()}catch(e){toast(e.message)}}
function setupRecognition(){const SR=window.SpeechRecognition||window.webkitSpeechRecognition;if(!SR){$('#micTop').disabled=true;$('#micDock').disabled=true;return}recognition=new SR();recognition.lang='pt-BR';recognition.interimResults=false;recognition.continuous=false;recognition.onstart=()=>{setState('listening','OUVINDO O ACH');$('#micTop').classList.add('active')};recognition.onresult=e=>{const text=e.results[0][0].transcript;$('#chatInput').value=text;sendChat()};recognition.onerror=e=>{toast(`Microfone: ${e.error}`);setState('idle','EM ESPERA')};recognition.onend=()=>{$('#micTop').classList.remove('active');if(!speaking&&!$('#avatarStage').classList.contains('thinking'))setState('idle','EM ESPERA')}}
function startMic(){if(recognition)try{recognition.start()}catch(e){}}
$('#sendBtn').onclick=sendChat;$('#chatInput').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendChat()}});$('#focusChat').onclick=()=>$('#chatInput').focus();$('#planNow').onclick=()=>{$('#chatInput').value='Hakham, organize nossas prioridades atuais em um plano objetivo para hoje.';sendChat()};$('#showHelp').onclick=()=>{$('#chatInput').value='/help';sendChat()};$('#micTop').onclick=startMic;$('#micDock').onclick=startMic;$('#stopVoice').onclick=()=>stopVoice();$('#voiceToggle').onclick=()=>{voiceEnabled=!voiceEnabled;$('#voiceToggle').classList.toggle('active',voiceEnabled);$('#voiceToggle').textContent=voiceEnabled?'🔊 VOZ ON':'🔇 VOZ OFF';if(!voiceEnabled)stopVoice();};$$('.modebtn').forEach(b=>b.onclick=()=>setMode(b.dataset.mode));$('#globalSearch').addEventListener('keydown',async e=>{if(e.key==='Enter'){const q=e.target.value.trim();if(!q)return;const r=await fetch('/api/memory/search?q='+encodeURIComponent(q)+'&limit=8'),d=await r.json();addMsg('MEMÓRIA',d.items?.length?d.items.map(i=>'• '+i.content).join('\n'):'Nada encontrado.')}});window.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();$('#globalSearch').focus()}});
setupRecognition();Promise.all([loadStatus(),loadList('/api/tasks?limit=5','#tasksList','tasks'),loadList('/api/projects?limit=5','#projectsList','projects'),loadList('/api/memory/recent?limit=5','#memoryList','memory'),loadAgents(),loadTools()]);
</script>
</body></html>'''