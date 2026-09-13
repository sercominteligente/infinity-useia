from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse, Response
from pydantic import BaseModel, Field

from . import web as backend
from . import web_v4 as previous
from .agents import AgentRegistry
from .tool_gateway import ToolGateway


app = FastAPI(title="HAKHAM Infinity Control Center", version="0.5.0")
agents = AgentRegistry()


class ToolExecuteRequest(BaseModel):
    tool_id: str = Field(min_length=2, max_length=128)
    arguments: dict[str, object] = Field(default_factory=dict)
    approved: bool = False


class AgentTaskRequest(BaseModel):
    agent_id: str = Field(min_length=2, max_length=64)
    message: str = Field(min_length=1, max_length=20_000)


def _avatar_file() -> Path:
    configured = os.getenv("HAKHAM_AVATAR_FILE", "").strip()
    return Path(configured) if configured else Path("assets/hakham-avatar.webp")


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return CONTROL_CENTER_HTML


@app.get("/assets/hakham-avatar")
def avatar_asset() -> FileResponse:
    path = _avatar_file()
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Hakham avatar asset is not installed")
    suffix = path.suffix.casefold()
    media_type = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }.get(suffix, "application/octet-stream")
    return FileResponse(path, media_type=media_type, headers={"Cache-Control": "no-cache"})


@app.get("/api/status")
def status() -> dict[str, object]:
    payload = previous.status()
    gateway = ToolGateway()
    local_avatar = _avatar_file().is_file()
    external_avatar = os.getenv("HAKHAM_AVATAR_URL", "").strip()
    payload.update(
        {
            "version": "0.5.0",
            "avatar_url": external_avatar or ("/assets/hakham-avatar" if local_avatar else ""),
            "avatar_ready": bool(external_avatar or local_avatar),
            "agent_count": len(agents.all()),
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
    return previous.chat(request)


@app.post("/api/voice/speech")
def speech(request: previous.SpeechRequest) -> Response:
    return previous.speech(request)


@app.get("/api/agents")
def list_agents() -> dict[str, object]:
    return {"items": agents.as_dicts()}


@app.post("/api/agents/delegate")
def delegate_agent(request: AgentTaskRequest) -> dict[str, object]:
    agent = agents.get(request.agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail=f"unknown agent: {request.agent_id}")
    if agent.role == "orchestrator":
        raise HTTPException(status_code=400, detail="delegate specialist work to a specialist agent")
    try:
        state = backend.runtime.state()
        prompt = agents.prompt_for(agent.id, request.message)
        answer = state.core.router.generate(state.core.provider, prompt)
        state.core.working.set(f"agent:{agent.id}", f"{agent.name}: {answer}")
        state.core.episodic.append("tool", f"Delegação para {agent.name}: {request.message}", session_id=state.core.session_id)
        state.core.episodic.append("tool", f"Resultado de {agent.name}: {answer}", session_id=state.core.session_id)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Agent unavailable: {exc}") from exc
    return {"agent": agent.id, "name": agent.name, "answer": answer}


@app.get("/api/tools")
def list_tools() -> dict[str, object]:
    return ToolGateway().summary()


@app.post("/api/tools/execute")
def execute_tool(request: ToolExecuteRequest) -> dict[str, object]:
    try:
        result = ToolGateway().execute(request.tool_id, request.arguments, approved=request.approved)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Tool execution failed: {exc}") from exc
    return {"tool_id": request.tool_id, "ok": True, "result": result}


def main() -> None:
    import uvicorn

    uvicorn.run("hakham.web_v5:app", host="127.0.0.1", port=8765, reload=False)


PREMIUM_STYLE = r'''
<style>
:root{--gold:#ffbd4a;--cyan2:#6ff4ff;--glass:#071522c9;--hud:#0b2438cc}
body:before{content:'';position:fixed;inset:0;pointer-events:none;background:radial-gradient(circle at 70% 16%,#0ac6ff10,transparent 22%),radial-gradient(circle at 18% 88%,#ffb84a0b,transparent 20%);z-index:-1}
.hero{border-color:#1b86ba;box-shadow:0 0 70px #0872b538 inset,0 16px 60px #000b,0 0 0 1px #6eeeff0d}.hero:after{content:'';position:absolute;inset:8px;pointer-events:none;border:1px solid #6eeeff17;clip-path:polygon(0 0,13% 0,14% 2px,86% 2px,87% 0,100% 0,100% 100%,87% 100%,86% calc(100% - 2px),14% calc(100% - 2px),13% 100%,0 100%)}
.card{backdrop-filter:blur(16px);box-shadow:0 10px 32px #0007,0 0 35px #0abfff0b inset;transition:.2s}.card:hover{border-color:#1871a6;box-shadow:0 12px 38px #0009,0 0 45px #0abfff12 inset;transform:translateY(-1px)}
.portrait-core{width:252px;height:252px;background:radial-gradient(circle at 50% 42%,#174e6c 0,#071725 42%,#01060d 73%);box-shadow:0 0 70px #0bd8ff7d,0 0 130px #007dcc4a inset}.portrait-core:before{inset:-31px;border-width:2px;box-shadow:0 0 18px #16d5ff55}.portrait-core:after{inset:-61px;border-color:#ffbd4a40}
.elder{width:208px;height:208px;display:grid;place-items:center;font-size:102px;border-radius:50%;overflow:visible;animation:hakhamBreath 5.6s ease-in-out infinite;transform-origin:50% 70%}.elder img{width:100%;height:100%;object-fit:contain;filter:drop-shadow(0 0 18px #1bd9ff88);display:none}.portrait-zone.listening .elder{animation:hakhamListen 1.2s ease-in-out infinite}.portrait-zone.thinking .elder{animation:hakhamThink 2.8s ease-in-out infinite}.portrait-zone.speaking .elder{animation:hakhamSpeak .72s ease-in-out infinite}.mouth-energy{position:absolute;left:50%;top:56%;width:48px;height:8px;transform:translate(-50%,-50%);border-radius:999px;background:#14e4ff;filter:blur(4px);opacity:0;box-shadow:0 0 22px #14e4ff}.portrait-zone.speaking .mouth-energy{opacity:.45;animation:mouthPulse .18s ease-in-out infinite alternate}.voice-reactor{position:absolute;left:50%;bottom:0;transform:translateX(-50%);width:min(470px,86%);height:84px;z-index:2}.voice-reactor canvas{width:100%;height:100%;filter:drop-shadow(0 0 10px #19dfffaa)}.voice-reactor:before,.voice-reactor:after{content:'';position:absolute;left:4%;right:4%;height:1px;background:linear-gradient(90deg,transparent,#16ddff,transparent)}.voice-reactor:before{top:18px}.voice-reactor:after{bottom:15px}.hud-corners{position:absolute;inset:11px;pointer-events:none;background:linear-gradient(var(--cyan),var(--cyan)) left top/34px 1px no-repeat,linear-gradient(var(--cyan),var(--cyan)) left top/1px 34px no-repeat,linear-gradient(var(--cyan),var(--cyan)) right top/34px 1px no-repeat,linear-gradient(var(--cyan),var(--cyan)) right top/1px 34px no-repeat,linear-gradient(var(--gold),var(--gold)) left bottom/28px 1px no-repeat,linear-gradient(var(--gold),var(--gold)) right bottom/28px 1px no-repeat;opacity:.65}.integrations-strip{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px}.mini-hud{border:1px solid #104d75;border-radius:14px;background:linear-gradient(180deg,#071827dc,#03101be8);padding:15px;box-shadow:0 0 30px #08a4e710 inset}.mini-hud h3{margin:0 0 12px;font-size:13px;letter-spacing:.1em;color:#d7f5ff}.agent-grid,.tool-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}.agent-tile,.tool-tile{border:1px solid #124668;border-radius:10px;background:#071a28;padding:10px;min-height:82px;transition:.2s}.agent-tile[data-agent]:hover{border-color:#20dcff;box-shadow:0 0 20px #0ad7ff1c;cursor:pointer}.agent-tile strong,.tool-tile strong{display:block;font-size:12px}.agent-tile small,.tool-tile small{color:#7399ae;font-size:10px}.perm{display:inline-block;margin-top:7px;padding:2px 7px;border-radius:999px;font-size:9px;border:1px solid #244}.perm.green{color:#1df2b0;border-color:#1df2b055}.perm.yellow{color:#ffbd4a;border-color:#ffbd4a55}.perm.red{color:#ff627d;border-color:#ff627d55}.tool-state{float:right;font-size:9px}.tool-state.ready{color:#1df2b0}.tool-state.off{color:#6c8798}.avatar-note{position:absolute;top:18px;left:50%;transform:translateX(-50%);font-size:9px;color:#6d93a8;letter-spacing:.08em}
@keyframes hakhamBreath{0%,100%{transform:translateY(3px) scale(1)}50%{transform:translateY(-2px) scale(1.012)}}@keyframes hakhamListen{0%,100%{transform:rotate(-.6deg) scale(1.012)}50%{transform:rotate(.8deg) scale(1.026)}}@keyframes hakhamThink{0%,100%{transform:translateY(1px)}50%{transform:translateY(-4px) rotate(.5deg)}}@keyframes hakhamSpeak{0%,100%{transform:translateY(1px) scale(1.01)}50%{transform:translateY(-2px) scale(1.025)}}@keyframes mouthPulse{from{transform:translate(-50%,-50%) scaleX(.45)}to{transform:translate(-50%,-50%) scaleX(1.2)}}
@media(max-width:900px){.integrations-strip{grid-template-columns:1fr}.agent-grid,.tool-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
</style>
'''

PREMIUM_UI = r'''
<script>
const premiumHero=document.querySelector('.hero');if(premiumHero){const c=document.createElement('div');c.className='hud-corners';premiumHero.appendChild(c)}
const elder=document.querySelector('#hakhamAvatar');if(elder){elder.innerHTML='<span class="avatar-fallback">🧙‍♂️</span><img id="hakhamOfficialAvatar" alt="Hakham">';const mouth=document.createElement('span');mouth.className='mouth-energy';elder.parentElement.appendChild(mouth)}
const portrait=document.querySelector('#portraitZone');if(portrait){const note=document.createElement('div');note.className='avatar-note';note.id='avatarNote';note.textContent='AVATAR INTERATIVO';portrait.appendChild(note);const vr=document.createElement('div');vr.className='voice-reactor';vr.innerHTML='<canvas id="voiceScope" width="900" height="150"></canvas>';portrait.appendChild(vr)}
const grid=document.querySelector('.grid');if(grid){const wrap=document.createElement('section');wrap.className='integrations-strip';wrap.innerHTML='<article class="mini-hud"><h3>⌘ EQUIPE DE AGENTES <span id="agentStatus" class="muted"></span></h3><div class="agent-grid" id="agentGrid"><div class="empty">Carregando agentes...</div></div></article><article class="mini-hud"><h3>⚙ TOOL GATEWAY <span id="toolStatus" class="muted"></span></h3><div class="tool-grid" id="toolGrid"><div class="empty">Carregando ferramentas...</div></div></article>';grid.parentElement.insertBefore(wrap,grid.nextSibling)}

let voiceAudioContext=null,voiceAnalyser=null,voiceSource=null;
function drawVoiceScope(){const canvas=document.querySelector('#voiceScope');if(!canvas)return;const ctx=canvas.getContext('2d');const w=canvas.width,h=canvas.height;ctx.clearRect(0,0,w,h);let data=null;if(voiceAnalyser){data=new Uint8Array(voiceAnalyser.frequencyBinCount);voiceAnalyser.getByteFrequencyData(data)}const zone=document.querySelector('#portraitZone');const speaking=zone?.classList.contains('speaking');const listening=zone?.classList.contains('listening');ctx.lineWidth=2;ctx.strokeStyle=listening?'#1df2b0':'#20e4ff';ctx.beginPath();for(let x=0;x<w;x+=5){const i=data?Math.floor(x/w*data.length):0;const raw=data?data[i]/255:((speaking||listening)?(0.28+Math.sin(Date.now()/120+x*.05)*.14):.06);const envelope=Math.sin(Math.PI*x/w);const amp=raw*58*envelope;const y=h/2+(x%10===0?1:-1)*amp;ctx.lineTo(x,y)}ctx.stroke();ctx.strokeStyle='rgba(255,189,74,.45)';ctx.beginPath();for(let x=0;x<w;x+=9){const y=h/2+Math.sin(Date.now()/260+x*.035)*8;ctx.lineTo(x,y)}ctx.stroke();requestAnimationFrame(drawVoiceScope)}drawVoiceScope();
function attachAnalyser(audio){try{voiceAudioContext=voiceAudioContext||new(window.AudioContext||window.webkitAudioContext)();if(voiceAudioContext.state==='suspended')voiceAudioContext.resume();voiceAnalyser=voiceAudioContext.createAnalyser();voiceAnalyser.fftSize=256;voiceSource=voiceAudioContext.createMediaElementSource(audio);voiceSource.connect(voiceAnalyser);voiceAnalyser.connect(voiceAudioContext.destination)}catch(e){voiceAnalyser=null}}
const basePlayHakhamAudio=playHakhamAudio;
playHakhamAudio=async function(item,generation){
  if(generation!==hakhamSpeechGeneration){URL.revokeObjectURL(item.url);throw new Error('speech-cancelled')}
  const audio=new Audio(item.url);audio.preload='auto';hakhamNaturalAudio=audio;attachAnalyser(audio);
  await new Promise((resolve,reject)=>{audio.onended=resolve;audio.onerror=()=>reject(new Error('falha ao reproduzir áudio'));audio.play().catch(reject)});
  URL.revokeObjectURL(item.url);hakhamNaturalAudio=null;voiceAnalyser=null;voiceSource=null;
};

async function loadPremiumStatus(){try{const r=await fetch('/api/status'),s=await r.json();const img=document.querySelector('#hakhamOfficialAvatar'),fallback=document.querySelector('.avatar-fallback'),note=document.querySelector('#avatarNote');if(img&&s.avatar_url){img.src=s.avatar_url;img.onload=()=>{img.style.display='block';if(fallback)fallback.style.display='none';if(note)note.textContent='HAKHAM · AVATAR OFICIAL'}}else if(note){note.textContent='ADICIONE assets/hakham-avatar.webp'}}catch(e){}}
async function loadAgents(){try{const r=await fetch('/api/agents'),d=await r.json();document.querySelector('#agentStatus').textContent=`${d.items.length} online`;document.querySelector('#agentGrid').innerHTML=d.items.map(a=>`<div class="agent-tile" ${a.role==='specialist'?`data-agent="${esc(a.id)}"`:''}><strong>${esc(a.icon)} ${esc(a.name)}</strong><small>${esc(a.specialty)}</small><span class="perm green">${a.role==='orchestrator'?'ORQUESTRADOR':'DELEGÁVEL'}</span></div>`).join('');document.querySelectorAll('.agent-tile[data-agent]').forEach(tile=>tile.onclick=()=>{const id=tile.dataset.agent;const name=tile.querySelector('strong').textContent.trim();const task=prompt(`Qual missão vamos delegar para ${name}?`);if(task)delegateAgent(id,task)})}catch(e){document.querySelector('#agentGrid').innerHTML='<div class="empty">Agentes indisponíveis.</div>'}}
async function delegateAgent(agentId,message){setHakhamState('thinking','DELEGANDO MISSÃO');toast('Agente em missão...');try{const r=await fetch('/api/agents/delegate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({agent_id:agentId,message})}),d=await r.json();if(!r.ok)throw new Error(d.detail||'falha');addMsg(d.name,d.answer);toast(`${d.name} concluiu a missão`)}catch(e){toast(e.message)}finally{setHakhamState('idle','EM ESPERA')}}
async function loadTools(){try{const r=await fetch('/api/tools'),d=await r.json();document.querySelector('#toolStatus').textContent=`${d.configured}/${d.items.length} configuradas`;document.querySelector('#toolGrid').innerHTML=d.items.map(t=>`<div class="tool-tile"><span class="tool-state ${t.configured?'ready':'off'}">${t.configured?'CONFIGURADA':'CONFIGURAR'}</span><strong>${esc(t.name)}</strong><small>${esc(t.description)}</small><span class="perm ${esc(t.permission)}">${t.permission.toUpperCase()}</span></div>`).join('')}catch(e){document.querySelector('#toolGrid').innerHTML='<div class="empty">Gateway indisponível.</div>'}}
Promise.all([loadPremiumStatus(),loadAgents(),loadTools()]);
</script>
'''

CONTROL_CENTER_HTML = (
    previous.CONTROL_CENTER_HTML
    .replace("HAKHAM INFINITY ∞ v0.4.1", "HAKHAM INFINITY ∞ v0.5")
    .replace("HAKHAM INFINITY ∞ v0.4", "HAKHAM INFINITY ∞ v0.5")
    .replace("</head>", PREMIUM_STYLE + "\n</head>")
    .replace("</body>", PREMIUM_UI + "\n</body>")
)
