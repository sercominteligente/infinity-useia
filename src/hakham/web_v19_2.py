from __future__ import annotations

from . import web_v19_1 as previous


app = previous.app

REFINEMENT_UI = r"""
<style id="hakham-v19-2-embedded-reactor">
/* v0.19.2: the reactor now sits over the infinity symbol already printed in
   Hakham's official artwork. The artwork remains the visual source of truth;
   the SVG contributes only a reactive energy trace. */
body.contextual-ready #hakhamCore .avatar-shell{padding-bottom:0!important}
.infinity-reactor{
  width:clamp(250px,43%,365px)!important;
  height:auto!important;
  aspect-ratio:360/190;
  bottom:6.5%!important;
  z-index:6!important;
  opacity:.94;
  mix-blend-mode:screen;
  filter:drop-shadow(0 0 calc(7px + var(--ir-energy)*18px) rgba(37,220,255,.42))!important;
}
.infinity-reactor svg{width:100%!important;height:100%!important}
.infinity-reactor .ir-shadow{display:none!important}
.infinity-reactor .ir-halo{stroke-width:5.4!important;opacity:calc(.05 + var(--ir-energy)*.18)!important;filter:blur(3px)!important}
.infinity-reactor .ir-track{stroke-width:1.65!important;stroke:rgba(132,232,255,.24)!important}
.infinity-reactor .ir-flow{stroke-width:2.65!important;filter:drop-shadow(0 0 4px rgba(37,220,255,.92))!important}
.infinity-reactor .ir-pulse{stroke-width:1.35!important;filter:drop-shadow(0 0 3px rgba(244,183,91,.55))!important}
.infinity-reactor .ir-node,.infinity-reactor .ir-center{opacity:.28!important}
.infinity-reactor .ir-state{display:none!important}
#hakhamCore[data-state="listening"] .infinity-reactor{filter:drop-shadow(0 0 calc(8px + var(--ir-energy)*22px) rgba(39,224,173,.54))!important}
#hakhamCore[data-state="thinking"] .infinity-reactor{filter:drop-shadow(0 0 calc(8px + var(--ir-energy)*21px) rgba(154,112,255,.50))!important}
#hakhamCore[data-state="speaking"] .infinity-reactor{filter:drop-shadow(0 0 calc(10px + var(--ir-energy)*26px) rgba(37,220,255,.68))!important}
#hakhamCore[data-state="executing"] .infinity-reactor{filter:drop-shadow(0 0 calc(9px + var(--ir-energy)*23px) rgba(244,183,91,.54))!important}

.context-window[data-kind="agents"]{--accent:#25dcff}
.context-window[data-kind="tools"]{--accent:#f4c45b}
.context-window[data-kind="status"]{--accent:#27e0ad}
.context-window[data-kind="projects"]{--accent:#62b7ff}
.context-window[data-kind="memory"]{--accent:#b590ff}
.cw-agent-grid,.cw-local-list{display:grid;gap:8px}
.cw-agent{width:100%;text-align:left;padding:10px 11px;border:1px solid rgba(86,176,214,.18);border-radius:11px;background:rgba(3,18,31,.56);color:#dff6ff;cursor:pointer}
.cw-agent:hover{border-color:color-mix(in srgb,var(--accent) 56%,transparent);background:rgba(7,31,49,.72)}
.cw-agent b{display:block;font-size:13px;color:#fff}.cw-agent small{display:block;margin-top:3px;color:#86a7b8;font-size:11px;line-height:1.4}.cw-agent span{display:block;margin-top:6px;color:var(--accent);font-size:9px;font-weight:850;letter-spacing:.08em}
.cw-local-row{padding:9px 10px;border:1px solid rgba(87,151,181,.15);border-radius:10px;background:rgba(3,17,29,.48)}
.cw-local-row b{display:block;color:#eefaff;font-size:12px}.cw-local-row small{display:block;color:#819eae;font-size:10px;margin-top:3px;overflow-wrap:anywhere}
.cw-kv{display:grid;grid-template-columns:minmax(100px,.7fr) minmax(0,1.3fr);gap:7px 10px;padding:7px 0;border-bottom:1px solid rgba(91,148,174,.13)}.cw-kv:last-child{border-bottom:0}.cw-kv span:first-child{color:#7898aa;font-size:10px;letter-spacing:.05em}.cw-kv span:last-child{color:#e5f7ff;font-size:11px;overflow-wrap:anywhere}

@media(max-width:900px){
 .infinity-reactor{width:clamp(195px,48vw,300px)!important;bottom:6.8%!important}
}
@media(max-width:520px){
 .infinity-reactor{width:clamp(180px,58vw,235px)!important;bottom:7.2%!important}
}
</style>
"""

REFINEMENT_SCRIPT = r"""
<script id="hakham-v19-2-local-context-windows-js">
(function(){
  const workspace=document.querySelector('#contextWorkspace');
  const minibar=document.querySelector('#contextMinibar');
  const input=document.querySelector('#chatInput');
  const sendButton=document.querySelector('#sendBtn');
  if(!workspace||!input||!sendButton)return;

  const localWindows=new Map();
  function esc(value){return String(value??'').replace(/[&<>"']/g,function(m){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot',"'":'&#39;'}[m]})}
  function clean(value){return String(value||'').replace(/\s+/g,' ').trim()}

  function localIntent(text){
    const t=clean(text);const low=t.toLocaleLowerCase('pt-BR');
    const command='(?:mostre(?:-me)?|mostrar|abra|abrir|liste|listar|quais|veja|ver|exiba|exibir)';
    if(new RegExp(command+'.{0,34}(?:nossos\\s+)?agentes|^(?:nossos\\s+)?agentes$|conselho de agentes','i').test(low))return{kind:'agents',icon:'⌘',title:'AGENTES HAKHAM',detail:'CONSELHO // ESPECIALISTAS'};
    if(new RegExp(command+'.{0,34}(?:ferramentas|tools?|tool gateway)|^(?:ferramentas|tools?)$','i').test(low))return{kind:'tools',icon:'⚙',title:'TOOL GATEWAY',detail:'FERRAMENTAS // CAPACIDADES'};
    if(new RegExp(command+'.{0,34}(?:status|estado do sistema)|^(?:status|status do sistema)$','i').test(low))return{kind:'status',icon:'◉',title:'STATUS DO SISTEMA',detail:'HAKHAM // RUNTIME'};
    if(new RegExp(command+'.{0,34}(?:nossos\\s+)?projetos|^(?:nossos\\s+)?projetos$','i').test(low))return{kind:'projects',icon:'◇',title:'PROJETOS',detail:'MEMÓRIA // PROJETOS ATIVOS'};
    if(new RegExp(command+'.{0,34}(?:mem[oó]ria|mem[oó]rias)|^(?:mem[oó]ria|mem[oó]rias)$','i').test(low))return{kind:'memory',icon:'▣',title:'MEMÓRIA HAKHAM',detail:'CONTEXTO // RECENTE'};
    return null;
  }

  function place(win){
    if(window.innerWidth<=900)return;
    const count=localWindows.size;win.style.top=(38+(count%3)*52)+'px';
    if(count%2===0){win.style.left=(16+(count%3)*24)+'px';win.style.right='auto'}else{win.style.right=(16+(count%3)*24)+'px';win.style.left='auto'}
  }

  function makeDraggable(win,head){
    let moving=false,dx=0,dy=0;
    head.addEventListener('pointerdown',function(event){if(window.innerWidth<=900||event.target.closest('button'))return;const rect=win.getBoundingClientRect();moving=true;dx=event.clientX-rect.left;dy=event.clientY-rect.top;win.style.left=rect.left+'px';win.style.top=rect.top+'px';win.style.right='auto';head.setPointerCapture(event.pointerId)});
    head.addEventListener('pointermove',function(event){if(!moving)return;const maxX=window.innerWidth-win.offsetWidth-8,maxY=window.innerHeight-win.offsetHeight-86;win.style.left=Math.max(8,Math.min(maxX,event.clientX-dx))+'px';win.style.top=Math.max(70,Math.min(maxY,event.clientY-dy))+'px'});
    head.addEventListener('pointerup',function(event){moving=false;try{head.releasePointerCapture(event.pointerId)}catch(e){}});
  }

  function minimize(win){
    win.classList.add('minimized');
    let tab=minibar&&minibar.querySelector('[data-local-restore="'+win.id+'"]');
    if(!tab&&minibar){tab=document.createElement('button');tab.className='context-tab';tab.dataset.localRestore=win.id;tab.textContent=(win.dataset.icon||'◉')+' '+(win.dataset.title||'JANELA');tab.onclick=function(){win.classList.remove('minimized');tab.remove()};minibar.appendChild(tab)}
  }

  function close(win){const tab=minibar&&minibar.querySelector('[data-local-restore="'+win.id+'"]');if(tab)tab.remove();localWindows.delete(win.dataset.kind);win.remove()}

  function openWindow(spec,query){
    let win=localWindows.get(spec.kind)||workspace.querySelector('.context-window[data-kind="'+spec.kind+'"]');
    if(win){win.classList.remove('minimized');const q=win.querySelector('.cw-query');if(q)q.textContent=query;const s=win.querySelector('.cw-status');if(s)s.textContent='CARREGANDO';return win}
    win=document.createElement('section');win.className='context-window';win.id='cw-local-'+spec.kind+'-'+Date.now();win.dataset.kind=spec.kind;win.dataset.icon=spec.icon;win.dataset.title=spec.title;
    win.innerHTML='<header class="cw-head"><div class="cw-icon">'+esc(spec.icon)+'</div><div class="cw-title"><b>'+esc(spec.title)+'</b><small>'+esc(spec.detail)+'</small></div><span class="cw-status">CARREGANDO</span><button class="cw-btn" data-min title="Minimizar">−</button><button class="cw-btn" data-close title="Fechar">×</button></header><div class="cw-body"><div class="cw-query"></div><div class="cw-data"><div class="cw-loading"><span class="cw-spinner"></span><span>Consultando o núcleo local...</span></div></div><div class="cw-section"><div class="cw-section-title">HAKHAM // CONTEXTO</div><div class="cw-answer"></div></div></div>';
    win.querySelector('.cw-query').textContent=query;workspace.appendChild(win);localWindows.set(spec.kind,win);place(win);makeDraggable(win,win.querySelector('.cw-head'));win.querySelector('[data-min]').onclick=function(){minimize(win)};win.querySelector('[data-close]').onclick=function(){close(win)};return win
  }

  async function api(url){const r=await fetch(url);let d={};try{d=await r.json()}catch(e){}if(!r.ok)throw new Error(d.detail||('HTTP '+r.status));return d}
  function ready(win,html){const data=win.querySelector('.cw-data');if(data)data.innerHTML=html;const status=win.querySelector('.cw-status');if(status)status.textContent='PRONTO'}
  function error(win,message){ready(win,'<div class="cw-answer">'+esc(message)+'</div>');const status=win.querySelector('.cw-status');if(status)status.textContent='ATENÇÃO'}

  async function hydrateAgents(win){
    try{const d=await api('/api/agents'),items=Array.isArray(d.items)?d.items:[];if(!items.length){ready(win,'<div class="cw-answer">Nenhum agente retornado pelo núcleo.</div>');return}
      const cards=items.map(function(a){const desc=a.description||a.specialty||a.role||'Especialista do ecossistema SER';return '<button class="cw-agent" data-agent="'+esc(a.id||'')+'"><b>'+esc(a.name||a.id||'Agente')+'</b><small>'+esc(desc)+'</small><span>DELEGAR MISSÃO →</span></button>'}).join('');ready(win,'<div class="cw-agent-grid">'+cards+'</div>');
      win.querySelectorAll('[data-agent]').forEach(function(button){button.onclick=function(){const id=button.dataset.agent||'';if(!id)return;input.value='/agent '+id+' ';input.focus();minimize(win)}})
    }catch(e){error(win,'Agentes indisponíveis: '+(e.message||e))}
  }

  async function hydrateTools(win){
    try{const d=await api('/api/tools'),items=Array.isArray(d.items)?d.items:[];const rows=items.map(function(t){return '<div class="cw-local-row"><b>'+esc(t.name||t.id)+'</b><small>'+esc((t.configured?'CONFIGURADA · ':'CONFIGURAR · ')+(t.description||''))+'</small></div>'}).join('');ready(win,'<div class="cw-local-list">'+(rows||'<div class="cw-answer">Nenhuma ferramenta retornada.</div>')+'</div>')}catch(e){error(win,'Tool Gateway indisponível: '+(e.message||e))}
  }

  async function hydrateStatus(win){
    try{const d=await api('/api/status');const fields=[['Estado',d.state||'online'],['Provider',d.provider||'—'],['Motor',d.model||'—'],['Modo',d.mode||'—'],['Memória',d.memory_db||'OK'],['Ferramentas',(d.tool_configured_count??'—')+'/'+(d.tool_count??'—')],['Versão',d.version||'—']];ready(win,fields.map(function(x){return '<div class="cw-kv"><span>'+esc(x[0])+'</span><span>'+esc(x[1])+'</span></div>'}).join(''))}catch(e){error(win,'Status indisponível: '+(e.message||e))}
  }

  async function hydrateList(win,url,emptyText){
    try{const d=await api(url),items=Array.isArray(d.items)?d.items:[];const rows=items.map(function(x){return '<div class="cw-local-row"><b>'+esc(x.content||x.name||'Item')+'</b><small>'+esc((x.kind||'')+(x.source?' · '+x.source:''))+'</small></div>'}).join('');ready(win,'<div class="cw-local-list">'+(rows||'<div class="cw-answer">'+esc(emptyText)+'</div>')+'</div>')}catch(e){error(win,'Dados indisponíveis: '+(e.message||e))}
  }

  async function hydrate(spec,win){
    if(spec.kind==='agents')return hydrateAgents(win);
    if(spec.kind==='tools')return hydrateTools(win);
    if(spec.kind==='status')return hydrateStatus(win);
    if(spec.kind==='projects')return hydrateList(win,'/api/projects?limit=12','Nenhum projeto consolidado na memória.');
    if(spec.kind==='memory')return hydrateList(win,'/api/memory/recent?limit=12','Ainda não há memórias duráveis para exibir.');
  }

  function caption(text){const c=document.querySelector('#hakhamCaption');if(!c)return;c.textContent=text;c.classList.add('show');clearTimeout(c._localHide);c._localHide=setTimeout(function(){c.classList.remove('show')},7000)}
  function say(answer){
    try{if(typeof addBubble==='function')addBubble('HAKHAM',answer)}catch(e){}
    caption(answer);
    try{if(typeof voiceEnabled==='undefined'||voiceEnabled){if(typeof speakHakham==='function')speakHakham(answer);else if(typeof setState==='function')setState('idle')}}catch(e){try{if(typeof setState==='function')setState('idle')}catch(_) {}}
  }

  async function handleLocal(text){
    const spec=localIntent(text);if(!spec)return false;
    input.value='';
    try{if(typeof addBubble==='function')addBubble('ACH',text)}catch(e){}
    try{if(typeof setState==='function')setState('executing','ABRINDO '+spec.title)}catch(e){}
    const win=openWindow(spec,text);await hydrate(spec,win);
    const answer={agents:'Claro, Ach. Estes são nossos agentes disponíveis. Clique em um deles para delegar uma missão.',tools:'Aqui está o Tool Gateway com as ferramentas disponíveis no Infinity.',status:'Aqui está o estado atual do núcleo do Hakham.',projects:'Aqui estão os projetos que estão consolidados na minha memória.',memory:'Aqui estão minhas memórias recentes.'}[spec.kind]||'Janela aberta, Ach.';
    const answerEl=win.querySelector('.cw-answer');if(answerEl)answerEl.textContent=answer;say(answer);return true
  }

  const previousSend=typeof window.sendChat==='function'?window.sendChat:null;
  async function v192Send(){const text=clean(input.value);if(!text)return;if(await handleLocal(text))return;if(previousSend)return previousSend()}
  window.sendChat=v192Send;try{sendChat=v192Send}catch(e){}
  sendButton.onclick=v192Send;
  input.addEventListener('keydown',function(event){if(event.key==='Enter'&&!event.shiftKey&&localIntent(input.value)){event.preventDefault();event.stopImmediatePropagation();v192Send()}},true);
})();
</script>
"""


def _enhance(html: str) -> str:
    html = html.replace("Orbit Command v0.19.1 Infinity Reactor", "Orbit Command v0.19.2 Embedded Reactor")
    html = html.replace("ORBIT COMMAND // v0.19.1 INFINITY REACTOR", "ORBIT COMMAND // v0.19.2 EMBEDDED REACTOR")
    html = html.replace("HAKHAM INFINITY ∞ v0.19.1 // SER Comtec", "HAKHAM INFINITY ∞ v0.19.2 // SER Comtec")
    html = html.replace("</head>", REFINEMENT_UI + "\n</head>")
    html = html.replace("</body>", REFINEMENT_SCRIPT + "\n</body>")
    return html


_stable_web = previous._stable_web
_stable_web.CONTROL_CENTER_HTML = _enhance(_stable_web.CONTROL_CENTER_HTML)
CONTROL_CENTER_HTML = _stable_web.CONTROL_CENTER_HTML


def main() -> None:
    import uvicorn

    uvicorn.run("hakham.web_v19_2:app", host="127.0.0.1", port=8765, reload=False)


if __name__ == "__main__":
    main()
