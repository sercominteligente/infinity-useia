from __future__ import annotations

from dataclasses import asdict
from threading import Lock

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from .cli import Runtime, build_runtime
from .config import load_settings
from .council import ModelCouncil
from .memory import MemoryStore
from .models import RouteLLMProvider


app = FastAPI(title="HAKHAM Infinity Control Center", version="0.2.0")


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=20_000)


class ModeRequest(BaseModel):
    mode: str = Field(min_length=3, max_length=20)


class ManualMemoryRequest(BaseModel):
    content: str = Field(min_length=1, max_length=5_000)
    kind: str = Field(default="fact", max_length=32)
    importance: int = Field(default=70, ge=0, le=100)


class RuntimeState:
    def __init__(self) -> None:
        self._runtime: Runtime | None = None
        self._lock = Lock()
        self._fingerprint: tuple[str, str, str] | None = None
        self._mode: str | None = None

    @staticmethod
    def _settings_fingerprint() -> tuple[str, str, str]:
        settings = load_settings()
        return (settings.model_provider, settings.model, settings.memory_db)

    @staticmethod
    def _mode_for_model(model: str) -> str:
        if model == "gpt-6-astra":
            return "astra"
        if model == "route-llm":
            return "auto"
        return "custom"

    def state(self) -> Runtime:
        fingerprint = self._settings_fingerprint()
        if self._runtime is None or self._fingerprint != fingerprint:
            with self._lock:
                if self._runtime is None or self._fingerprint != fingerprint:
                    self._runtime = build_runtime()
                    self._fingerprint = fingerprint
                    self._mode = self._mode_for_model(self._runtime.settings.model)
        return self._runtime

    def core(self):
        return self.state().core

    def mode(self) -> str:
        if self._runtime is not None:
            return self._mode or self._mode_for_model(self._runtime.core.model)
        settings = load_settings()
        return self._mode_for_model(settings.model)

    def set_mode(self, mode: str) -> dict[str, object]:
        mode = mode.strip().casefold()
        state = self.state()
        if state.abacus is None:
            raise ValueError("troca de motor no painel requer HAKHAM_MODEL_PROVIDER=abacus")
        if mode == "astra":
            state.abacus.model = "gpt-6-astra"
            state.core.model = "gpt-6-astra"
            self._mode = "astra"
        elif mode == "auto":
            state.abacus.model = "route-llm"
            state.core.model = "route-llm"
            self._mode = "auto"
        elif mode == "council":
            if len(state.settings.abacus_council_models) < 2:
                raise ValueError("configure pelo menos dois modelos em HAKHAM_COUNCIL_MODELS antes de ativar o Conselho")
            self._mode = "council"
        else:
            raise ValueError(f"modo desconhecido: {mode}")
        return self.summary()

    def summary(self) -> dict[str, object]:
        settings = load_settings()
        model = settings.model
        runtime_loaded = self._runtime is not None
        if self._runtime is not None:
            model = self._runtime.core.model
        council_ready = len(settings.abacus_council_models) >= 2
        return {
            "provider": settings.model_provider,
            "model": model,
            "memory_db": settings.memory_db,
            "abacus_key_configured": bool(settings.abacus_routellm_api_key),
            "runtime_loaded": runtime_loaded,
            "mode": self.mode(),
            "council_ready": council_ready,
            "council_models": list(settings.abacus_council_models),
        }


runtime = RuntimeState()


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return CONTROL_CENTER_HTML


@app.get("/api/status")
def status() -> dict[str, object]:
    return {
        "name": "HAKHAM Infinity",
        "version": "0.2.0",
        "state": "online",
        **runtime.summary(),
    }


@app.get("/api/memory/recent")
def recent_memory(limit: int = Query(default=8, ge=1, le=50)) -> dict[str, object]:
    settings = load_settings()
    memories = MemoryStore(settings.memory_db).recent(limit=limit)
    return {"items": [asdict(item) for item in memories]}


@app.get("/api/projects")
def projects(limit: int = Query(default=6, ge=1, le=30)) -> dict[str, object]:
    settings = load_settings()
    memories = MemoryStore(settings.memory_db).recent(limit=limit, kind="project")
    return {"items": [asdict(item) for item in memories]}


@app.get("/api/tasks")
def tasks(limit: int = Query(default=6, ge=1, le=30)) -> dict[str, object]:
    settings = load_settings()
    memories = MemoryStore(settings.memory_db).recent(limit=limit, kind="task")
    return {"items": [asdict(item) for item in memories]}


@app.post("/api/memory")
def create_memory(request: ManualMemoryRequest) -> dict[str, object]:
    settings = load_settings()
    try:
        memory = MemoryStore(settings.memory_db).remember(
            request.content,
            kind=request.kind,
            source="user-explicit",
            importance=request.importance,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"item": asdict(memory)}


@app.get("/api/memory/search")
def search_memory(
    q: str = Query(default="", max_length=500),
    limit: int = Query(default=8, ge=1, le=50),
) -> dict[str, object]:
    settings = load_settings()
    memories = MemoryStore(settings.memory_db).search(q, limit=limit)
    return {"items": [asdict(item) for item in memories]}


@app.get("/api/models")
def models() -> dict[str, object]:
    settings = load_settings()
    if settings.model_provider != "abacus":
        return {"provider": settings.model_provider, "items": []}
    if not settings.abacus_routellm_api_key:
        raise HTTPException(status_code=503, detail="Abacus key is not configured")
    provider = RouteLLMProvider(
        api_key=settings.abacus_routellm_api_key,
        model=settings.model,
        base_url=settings.abacus_routellm_base_url,
    )
    try:
        return {"provider": "abacus", "items": provider.list_models()}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"RouteLLM catalog unavailable: {exc}") from exc


@app.post("/api/mode")
def set_mode(request: ModeRequest) -> dict[str, object]:
    try:
        return runtime.set_mode(request.mode)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _council_answer(message: str) -> str:
    state = runtime.state()
    if state.abacus is None:
        raise ValueError("Conselho requer provider Abacus")
    models = list(state.settings.abacus_council_models)
    if len(models) < 2:
        raise ValueError("configure HAKHAM_COUNCIL_MODELS com pelo menos dois modelos")
    result = ModelCouncil(state.abacus).deliberate(
        message,
        models=models,
        synthesis_model=state.settings.abacus_synthesis_model,
    )
    answer = result.synthesis
    state.core.episodic.append("user", message, session_id=state.core.session_id)
    state.core.episodic.append("assistant", answer, session_id=state.core.session_id)
    state.core._remember_semantic_user_message(message)
    return answer


@app.post("/api/chat")
def chat(request: ChatRequest) -> dict[str, str]:
    message = request.message.strip()
    try:
        if runtime.mode() == "council":
            answer = _council_answer(message)
        else:
            answer = runtime.core().ask(message)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Hakham engine unavailable: {exc}") from exc
    return {"answer": answer}


def main() -> None:
    import uvicorn

    uvicorn.run("hakham.web:app", host="127.0.0.1", port=8765, reload=False)


CONTROL_CENTER_HTML = r'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>HAKHAM Infinity Control Center</title>
<style>
:root{color-scheme:dark;--bg:#020713;--bg2:#071528;--panel:#061323e8;--panel2:#081a2ee8;--line:#124d7d;--line2:#0d3658;--cyan:#12d9ff;--blue:#268cff;--text:#edf8ff;--muted:#7fa3bb;--ok:#1df2b0;--warn:#ffb74d;--purple:#8d5cff;--danger:#ff627d}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;min-height:100vh;background:radial-gradient(circle at 52% 0,#0d2e53 0,#051225 27%,#020711 66%);font-family:Inter,Segoe UI,system-ui,Arial,sans-serif;color:var(--text);overflow-x:hidden}button,input,textarea{font:inherit}.shell{display:grid;grid-template-columns:250px minmax(0,1fr);min-height:100vh}.side{position:sticky;top:0;height:100vh;padding:18px 14px;border-right:1px solid #0e3557;background:linear-gradient(180deg,#020917f5,#020711f0);box-shadow:12px 0 50px #00172c55;z-index:5}.brand{display:flex;gap:11px;align-items:center;padding:8px 8px 21px;border-bottom:1px solid #0c2a45;margin-bottom:14px}.brandmark{font-size:34px;color:var(--cyan);text-shadow:0 0 24px #10d7ff99}.brand strong{display:block;letter-spacing:.12em}.brand small{color:var(--cyan);font-size:10px}.nav{display:grid;gap:6px}.nav button{all:unset;display:flex;align-items:center;gap:12px;padding:13px 14px;border:1px solid transparent;border-radius:10px;color:#a9c8dc;cursor:pointer;transition:.2s}.nav button:hover,.nav .active{border-color:#176da8;background:linear-gradient(90deg,#0d3a5fbb,#08233a55);color:white;box-shadow:0 0 22px #0b76ba2e}.nav i{font-style:normal;width:22px;text-align:center;color:#69bfff}.quote{position:absolute;left:18px;right:18px;bottom:105px;padding:15px;border-top:1px solid #0e385c;border-bottom:1px solid #0e385c;color:#8bb3cd;font-size:12px;line-height:1.7;letter-spacing:.05em}.wolf{position:absolute;left:14px;right:14px;bottom:16px;padding:14px;border:1px solid #14547f;border-radius:14px;background:linear-gradient(135deg,#07182a,#04101e);box-shadow:0 0 28px #0c73b227 inset}.wolf-head{display:flex;align-items:center;gap:10px}.wolf-icon{width:42px;height:42px;border-radius:50%;display:grid;place-items:center;border:1px solid #2a8ac0;background:#091f33;font-size:24px}.wolf b{display:block}.online{color:var(--ok);font-size:11px}.main{min-width:0;padding:14px 18px 24px}.topbar{display:grid;grid-template-columns:1fr minmax(300px,610px) 1fr;align-items:center;gap:16px;margin-bottom:13px}.topbrand{font-size:12px;letter-spacing:.2em;color:#89b4ce}.search{position:relative}.search input{width:100%;height:42px;border:1px solid #14476e;border-radius:11px;background:#061323;color:#def5ff;padding:0 46px 0 42px;outline:none}.search:before{content:'⌕';position:absolute;left:14px;top:8px;font-size:22px;color:#7ebce0}.searchkbd{position:absolute;right:10px;top:10px;font-size:10px;border:1px solid #1a4b70;border-radius:6px;padding:3px 6px;color:#7399b2}.topright{justify-self:end;display:flex;gap:10px;align-items:center}.clock{text-align:right}.clock b{font-size:20px}.chip{border:1px solid #15547d;border-radius:999px;padding:7px 11px;background:#071729;color:#bdeeff;font-size:12px}.hero{position:relative;display:grid;grid-template-columns:1.05fr .95fr;min-height:330px;border:1px solid #13649a;border-radius:16px;overflow:hidden;background:radial-gradient(circle at 74% 42%,#0c477366 0,#071a2d 30%,#04101e 72%);box-shadow:0 0 55px #0872b528 inset,0 10px 50px #0008}.hero:before{content:'';position:absolute;inset:0;background-image:linear-gradient(#0b86c70b 1px,transparent 1px),linear-gradient(90deg,#0b86c70b 1px,transparent 1px);background-size:35px 35px;mask-image:linear-gradient(to right,transparent,#000,transparent)}.hero-copy{position:relative;z-index:2;padding:28px 30px}.eyebrow{color:var(--cyan);letter-spacing:.16em;font-size:12px}.hero h1{font-size:46px;line-height:1.03;margin:11px 0 8px;max-width:600px}.hero h1 em{font-style:normal;color:var(--cyan);text-shadow:0 0 24px #16caff55}.hero p{max-width:560px;color:#9ebed1;line-height:1.6;margin-bottom:21px}.hero-actions{display:flex;gap:10px;flex-wrap:wrap}.primary,.secondary{border-radius:10px;padding:11px 16px;cursor:pointer;font-weight:700;letter-spacing:.03em}.primary{border:1px solid #35e9ff;background:linear-gradient(90deg,#13aee0,#1680bd);color:#02121e;box-shadow:0 0 25px #18cfff55}.secondary{border:1px solid #1b608d;background:#07182a;color:#bfeeff}.portrait-zone{position:relative;display:grid;place-items:center;min-height:300px}.portrait-core{position:relative;width:225px;height:225px;border-radius:50%;display:grid;place-items:center;border:1px solid #16d5ff;background:radial-gradient(circle,#15537d 0,#08192b 44%,#020812 72%);box-shadow:0 0 55px #08aee988,0 0 95px #0a6da955 inset}.portrait-core:before,.portrait-core:after{content:'';position:absolute;border-radius:50%;border:1px solid #18ccff66;inset:-23px;animation:spin 14s linear infinite}.portrait-core:after{inset:-47px;border-style:dashed;animation-direction:reverse;animation-duration:23s}.elder{font-size:104px;filter:drop-shadow(0 0 18px #26bfff);transform:translateY(4px)}.reactor{position:absolute;bottom:26px;left:50%;transform:translateX(-50%);font-size:38px;color:#fff;text-shadow:0 0 20px #1de4ff}.wave{position:absolute;bottom:15px;left:15%;right:15%;height:20px;background:repeating-linear-gradient(90deg,transparent 0 8px,#1de3ff 8px 10px);mask-image:linear-gradient(to right,transparent,#000,transparent);opacity:.55;animation:pulse 1.3s ease-in-out infinite}.modebar{position:absolute;right:18px;top:18px;z-index:3;display:flex;gap:7px}.modebtn{border:1px solid #18547c;background:#061728;color:#78a8c4;border-radius:8px;padding:7px 10px;font-size:11px;cursor:pointer}.modebtn.active{color:#03111a;background:var(--cyan);border-color:#5deaff;font-weight:800}.modebtn:disabled{opacity:.35;cursor:not-allowed}.grid{display:grid;grid-template-columns:1.05fr 1.05fr .9fr;gap:12px;margin-top:12px}.card{position:relative;background:linear-gradient(180deg,var(--panel),#04101de8);border:1px solid #10456e;border-radius:14px;padding:15px;min-height:200px;overflow:hidden}.card:before{content:'';position:absolute;top:0;left:0;width:80px;height:1px;background:var(--cyan);box-shadow:0 0 13px var(--cyan)}.card h3{margin:0 0 13px;font-size:13px;letter-spacing:.08em;color:#d2edfb;display:flex;align-items:center;justify-content:space-between}.card h3 span{color:#4fb8f0;font-size:11px;font-weight:500}.row{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:9px 0;border-bottom:1px solid #0a2c49;font-size:12px}.row:last-child{border-bottom:0}.row-main{min-width:0}.row-title{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.row-sub{font-size:10px;color:var(--muted);margin-top:3px}.dot{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:7px;background:var(--ok);box-shadow:0 0 12px currentColor}.ok{color:var(--ok)}.muted{color:var(--muted)}.warn{color:var(--warn)}.purple{color:var(--purple)}.progress{height:6px;background:#0a2943;border-radius:999px;overflow:hidden;margin-top:6px}.progress i{display:block;height:100%;background:linear-gradient(90deg,#13c8ff,#2c7fff);border-radius:999px}.actions{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.action{border:1px solid #14486f;background:#071a2d;color:#c5e8fa;border-radius:10px;padding:13px 8px;text-align:center;cursor:pointer;font-size:11px}.action b{display:block;font-size:20px;color:#56cfff;margin-bottom:5px}.chat{grid-column:1/-1;min-height:300px}.messages{height:250px;overflow:auto;padding:3px 4px 5px}.msg{max-width:760px;padding:11px 13px;border:1px solid #164b71;border-radius:12px;margin:8px 0;background:#071b2e;white-space:pre-wrap;line-height:1.48;font-size:13px}.msg.user{margin-left:auto;background:#0d3153}.msg .who{font-size:10px;color:var(--cyan);margin-bottom:5px;letter-spacing:.08em}.composer{display:flex;gap:9px;margin-top:8px}.composer textarea{flex:1;background:#020913;border:1px solid #1d5b85;border-radius:11px;color:white;padding:12px;resize:vertical;min-height:50px;outline:none}.composer button{border:1px solid #2be5ff;background:#0b6fa1;color:white;border-radius:11px;padding:0 21px;font-weight:800;cursor:pointer}.composer button:disabled{opacity:.5}.empty{color:#6f91a7;font-size:12px;padding:10px 0}.toast{position:fixed;right:20px;bottom:20px;z-index:20;padding:12px 15px;border:1px solid #1d719f;background:#061a2b;border-radius:10px;color:#d9f5ff;box-shadow:0 0 35px #0009;opacity:0;transform:translateY(10px);pointer-events:none;transition:.2s}.toast.show{opacity:1;transform:none}.footer{display:flex;justify-content:space-between;color:#5f839a;font-size:10px;letter-spacing:.08em;padding:16px 4px 0}@keyframes spin{to{transform:rotate(360deg)}}@keyframes pulse{50%{opacity:.9;transform:scaleY(1.45)}}
@media(max-width:1180px){.grid{grid-template-columns:1fr 1fr}.grid>.card:nth-child(3){grid-column:1/-1}.hero{grid-template-columns:1fr .8fr}.hero h1{font-size:38px}.topbar{grid-template-columns:1fr 1.4fr}.topright{display:none}}
@media(max-width:820px){.shell{grid-template-columns:1fr}.side{display:none}.main{padding:10px}.topbar{grid-template-columns:1fr}.topbrand{display:none}.hero{grid-template-columns:1fr;min-height:600px}.hero-copy{padding:22px}.hero h1{font-size:36px}.portrait-zone{min-height:280px}.grid{grid-template-columns:1fr}.grid>.card:nth-child(3){grid-column:auto}.chat{grid-column:auto}.modebar{top:auto;bottom:10px;right:10px}.actions{grid-template-columns:repeat(2,1fr)}}
</style>
</head>
<body>
<div class="shell">
<aside class="side">
  <div class="brand"><div class="brandmark">∞</div><div><strong>HAKHAM INFINITY</strong><small>PENSAR MAIS FUNDO. CONSTRUIR MAIS LONGE.</small></div></div>
  <nav class="nav"><button class="active"><i>⌂</i>Dashboard</button><button><i>▣</i>Memória</button><button><i>◇</i>Projetos</button><button><i>⌘</i>Agentes</button><button><i>⚙</i>Ferramentas</button><button><i>✓</i>Missões</button><button><i>◉</i>Configurações</button></nav>
  <div class="quote">“DISCIPLINA<br>EXECUÇÃO<br>RESULTADOS<br>SEMPRE.”<br><span class="muted">— ACH</span></div>
  <div class="wolf"><div class="wolf-head"><div class="wolf-icon">🐺</div><div><span class="online">● ONLINE</span><b>ACH</b><small class="muted">Modo Estratégico</small></div></div></div>
</aside>
<main class="main">
  <header class="topbar"><div class="topbrand">HAKHAM CONTROL CENTER</div><div class="search"><input id="globalSearch" placeholder="Buscar memórias, projetos, comandos..."><span class="searchkbd">Ctrl K</span></div><div class="topright"><div class="clock"><small id="dateLabel" class="muted"></small><br><b id="clockLabel"></b></div><span class="chip" id="providerBadge">carregando motor...</span></div></header>
  <section class="hero">
    <div class="modebar"><button class="modebtn" data-mode="astra">ASTRA</button><button class="modebtn" data-mode="auto">AUTO</button><button class="modebtn" data-mode="council">CONSELHO</button></div>
    <div class="hero-copy"><div class="eyebrow">∞ HAKHAM // COPILOTO ESTRATÉGICO</div><h1>Eaew Ach,<br>onde vamos <em>atacar hoje?</em></h1><p>Sua visão. Minha sabedoria. Memória viva, múltiplos motores e execução coordenada em um único centro de comando.</p><div class="hero-actions"><button class="primary" id="focusChat">▶ CONVERSAR COM HAKHAM</button><button class="secondary" id="planNow">ϟ PLANEJAR AGORA</button></div></div>
    <div class="portrait-zone"><div class="portrait-core"><div class="elder">🧙‍♂️</div><div class="reactor">∞</div></div><div class="wave"></div></div>
  </section>
  <section class="grid">
    <article class="card"><h3>✓ MISSÕES DO DIA <span id="taskCount"></span></h3><div id="taskRows"><div class="empty">Carregando missões...</div></div></article>
    <article class="card"><h3>◇ PROJETOS ATIVOS <span>memória semântica</span></h3><div id="projectRows"><div class="empty">Carregando projetos...</div></div></article>
    <article class="card"><h3>⌁ STATUS DO SISTEMA <span id="systemState" class="ok">OPERACIONAL</span></h3><div id="statusRows"><div class="empty">Carregando status...</div></div></article>
    <article class="card"><h3>▣ MEMÓRIAS RECENTES <span id="memoryCount"></span></h3><div id="memoryRows"><div class="empty">Carregando memórias...</div></div></article>
    <article class="card"><h3>✦ SUGESTÕES DO HAKHAM <span>próximos passos</span></h3><div id="suggestionRows"></div></article>
    <article class="card"><h3>ϟ AÇÕES RÁPIDAS <span>comando direto</span></h3><div class="actions"><button class="action" id="newMemory"><b>▣</b>Nova Memória</button><button class="action" id="openProjects"><b>◇</b>Projetos</button><button class="action" id="delegate"><b>⌘</b>Agentes</button><button class="action" id="analyze"><b>⌕</b>Analisar</button><button class="action" id="plan"><b>▥</b>Gerar Plano</button><button class="action" id="chatQuick"><b>◫</b>Chat Hakham</button></div></article>
    <article class="card chat" id="chatCard"><h3>◫ CHAT COM HAKHAM <span id="chatMode">modo atual</span></h3><div class="messages" id="messages"><div class="msg"><div class="who">HAKHAM</div>HAKHAM operacional. Propulsão online. Onde vamos atacar hoje, Ach?</div></div><div class="composer"><textarea id="message" placeholder="Fale com Hakham..."></textarea><button id="send">ENVIAR</button></div></article>
  </section>
  <footer class="footer"><span>HAKHAM INFINITY ∞ v0.2</span><span>SONHE. PLANEJE. EXECUTE. EVOLUA. ∞</span></footer>
</main>
</div>
<div class="toast" id="toast"></div>
<script>
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];let lastStatus=null;
function esc(s){return String(s).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]))}
function toast(text){const t=$('#toast');t.textContent=text;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),2600)}
function tick(){const d=new Date();$('#clockLabel').textContent=d.toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'});$('#dateLabel').textContent=d.toLocaleDateString('pt-BR',{weekday:'short',day:'2-digit',month:'short',year:'numeric'}).toUpperCase()}tick();setInterval(tick,1000);
async function loadStatus(){try{const r=await fetch('/api/status'),s=await r.json();lastStatus=s;$('#providerBadge').textContent=`${s.provider} · ${s.model}`;$('#chatMode').textContent=`${s.mode.toUpperCase()} · ${s.model}`;$('#statusRows').innerHTML=`<div class="row"><span>Core</span><span class="ok">${s.runtime_loaded?'CARREGADO':'STANDBY'}</span></div><div class="row"><span>Provider</span><span>${esc(s.provider)}</span></div><div class="row"><span>Motor</span><span class="ok">${esc(s.model)}</span></div><div class="row"><span>Memória</span><span class="ok">OK</span></div><div class="row"><span>Conselho</span><span class="${s.council_ready?'ok':'muted'}">${s.council_ready?'PRONTO':'CONFIGURAR'}</span></div>`;$$('.modebtn').forEach(b=>{b.classList.toggle('active',b.dataset.mode===s.mode);if(b.dataset.mode==='council')b.disabled=!s.council_ready});renderSuggestions(s)}catch(e){$('#systemState').textContent='INDISPONÍVEL';$('#systemState').className='warn'}}
async function loadMemory(){try{const r=await fetch('/api/memory/recent?limit=6'),d=await r.json();$('#memoryCount').textContent=`${d.items.length} exibidas`;$('#memoryRows').innerHTML=d.items.length?d.items.map(m=>`<div class="row"><div class="row-main"><div class="row-title">${esc(m.content).slice(0,78)}</div><div class="row-sub">${esc(m.kind)} · importância ${m.importance}</div></div><span class="muted">#${m.id}</span></div>`).join(''):'<div class="empty">Ainda sem memórias duráveis neste ambiente.</div>'}catch(e){$('#memoryRows').innerHTML='<div class="empty">Memória indisponível.</div>'}}
async function loadProjects(){try{const r=await fetch('/api/projects?limit=5'),d=await r.json();$('#projectRows').innerHTML=d.items.length?d.items.map((m,i)=>`<div class="row"><div class="row-main"><div class="row-title"><span class="dot ${i%2?'purple':''}"></span>${esc(m.content).slice(0,70)}</div><div class="row-sub">fonte ${esc(m.source)}</div></div><span class="ok">ATIVO</span></div>`).join(''):'<div class="empty">Nenhum projeto consolidado na memória ainda.</div>'}catch(e){$('#projectRows').innerHTML='<div class="empty">Projetos indisponíveis.</div>'}}
async function loadTasks(){try{const r=await fetch('/api/tasks?limit=5'),d=await r.json();const defaults=[];if(!d.items.length){defaults.push('Validar motor principal do HAKHAM','Evoluir interface do Control Center','Preparar Voice Loop e avatar interativo')}const items=d.items.map(x=>x.content).concat(defaults).slice(0,5);$('#taskCount').textContent=`${items.length} em foco`;$('#taskRows').innerHTML=items.map((x,i)=>`<div class="row"><div class="row-main"><div class="row-title">${i<1?'☑':'☐'} ${esc(x).slice(0,76)}</div><div class="progress"><i style="width:${i===0?100:i===1?62:24}%"></i></div></div><span class="${i===0?'ok':'muted'}">${i===0?'EM CURSO':'PRÓXIMO'}</span></div>`).join('')}catch(e){$('#taskRows').innerHTML='<div class="empty">Missões indisponíveis.</div>'}}
function renderSuggestions(s){const arr=[];if(s.model!=='gpt-6-astra')arr.push('Testar GPT-6 Astra como motor dedicado');if(!s.council_ready)arr.push('Configurar 2 ou 3 motores para o Modo Conselho');arr.push('Consolidar memórias relevantes do projeto','Preparar avatar interativo do Hakham','Ativar Voice Loop após estabilizar o painel');$('#suggestionRows').innerHTML=arr.slice(0,5).map((x,i)=>`<div class="row"><span>${i+1}. ${esc(x)}</span><span class="muted">›</span></div>`).join('')}
async function changeMode(mode){try{const r=await fetch('/api/mode',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode})}),d=await r.json();if(!r.ok)throw new Error(d.detail||'falha');toast(`Modo ${mode.toUpperCase()} ativado`);await loadStatus()}catch(e){toast(e.message)}}$$('.modebtn').forEach(b=>b.onclick=()=>changeMode(b.dataset.mode));
function addMsg(who,text,klass=''){const d=document.createElement('div');d.className='msg '+klass;d.innerHTML=`<div class="who">${esc(who)}</div>${esc(text)}`;$('#messages').appendChild(d);$('#messages').scrollTop=$('#messages').scrollHeight}
async function send(){const box=$('#message'),btn=$('#send'),message=box.value.trim();if(!message)return;addMsg('ACH',message,'user');box.value='';btn.disabled=true;try{const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message})}),d=await r.json();if(!r.ok)throw new Error(d.detail||'falha');addMsg('HAKHAM',d.answer);await Promise.all([loadStatus(),loadMemory(),loadProjects(),loadTasks()])}catch(e){addMsg('SISTEMA','Motor indisponível: '+e.message)}finally{btn.disabled=false;box.focus()}}
$('#send').onclick=send;$('#message').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send()}});function focusChat(prefill=''){document.querySelector('#chatCard').scrollIntoView({behavior:'smooth'});$('#message').focus();if(prefill)$('#message').value=prefill}$('#focusChat').onclick=()=>focusChat();$('#chatQuick').onclick=()=>focusChat();$('#planNow').onclick=()=>focusChat('Hakham, organize minhas prioridades e monte um plano objetivo para hoje.');$('#plan').onclick=$('#planNow').onclick;$('#analyze').onclick=()=>focusChat('Hakham, analise o estado atual dos nossos projetos e aponte riscos, gargalos e próximos passos.');$('#delegate').onclick=()=>focusChat('Hakham, qual agente especializado devemos acionar para a próxima missão?');$('#openProjects').onclick=()=>document.querySelector('#projectRows').scrollIntoView({behavior:'smooth'});
$('#newMemory').onclick=async()=>{const content=prompt('Qual memória explícita você quer registrar?');if(!content)return;try{const r=await fetch('/api/memory',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({content,kind:'fact',importance:80})}),d=await r.json();if(!r.ok)throw new Error(d.detail||'falha');toast('Memória registrada');loadMemory()}catch(e){toast(e.message)}};
$('#globalSearch').addEventListener('keydown',async e=>{if(e.key!=='Enter')return;const q=e.target.value.trim();if(!q)return;try{const r=await fetch('/api/memory/search?q='+encodeURIComponent(q)+'&limit=6'),d=await r.json();$('#memoryRows').innerHTML=d.items.length?d.items.map(m=>`<div class="row"><div class="row-main"><div class="row-title">${esc(m.content).slice(0,82)}</div><div class="row-sub">${esc(m.kind)} · ${esc(m.source)}</div></div></div>`).join(''):'<div class="empty">Nenhuma memória encontrada.</div>';document.querySelector('#memoryRows').scrollIntoView({behavior:'smooth'})}catch(err){toast('Busca indisponível')}});document.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();$('#globalSearch').focus()}});
Promise.all([loadStatus(),loadMemory(),loadProjects(),loadTasks()]);
</script>
</body></html>'''
