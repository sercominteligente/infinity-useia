from __future__ import annotations

from . import web_v17 as previous


app = previous.app

CONTEXTUAL_UI = r"""
<style id="hakham-v19-contextual-workspace">
:root{--cw-bg:rgba(3,13,25,.91);--cw-line:rgba(37,220,255,.28);--cw-line-strong:rgba(37,220,255,.62);--cw-shadow:0 28px 90px rgba(0,0,0,.52)}
body.contextual-ready{overflow:hidden}
body.contextual-ready .topbar{min-height:64px;padding:8px 14px;background:rgba(1,6,14,.76);border-bottom-color:rgba(37,220,255,.15);box-shadow:0 8px 36px rgba(0,0,0,.22)}
body.contextual-ready .topcenter{display:none!important}
body.contextual-ready .brandbar{min-width:0;gap:12px}
body.contextual-ready .brand-infinity{font-size:31px}
body.contextual-ready .hakham-brand b{font-size:15px}
body.contextual-ready .hakham-brand small{font-size:10px}
body.contextual-ready .brand-divider{height:31px}
body.contextual-ready .sercomtec{height:28px;max-width:142px}
body.contextual-ready .topright{gap:8px}
body.contextual-ready .clock{display:none}
body.contextual-ready .engine{min-width:112px;padding:6px 9px;font-size:11px;background:rgba(4,20,34,.56)}
body.contextual-ready .mode-group{padding:3px;background:rgba(3,14,25,.52)}
body.contextual-ready .modebtn{padding:6px 9px;font-size:11px}
body.contextual-ready .page{width:100%;max-width:none;margin:0;padding:0;min-height:calc(100vh - 64px)}
body.contextual-ready .stage{display:block!important;position:relative;min-height:calc(100vh - 64px)}
body.contextual-ready .stage>.left,body.contextual-ready .stage>.right{display:none!important}
body.contextual-ready #hakhamCore{display:flex!important;width:100%;min-height:calc(100vh - 64px)!important;padding:8px 18px 110px!important;border:0!important;border-radius:0!important;box-shadow:none!important;backdrop-filter:none!important;overflow:visible!important;background:radial-gradient(circle at 50% 42%,rgba(18,164,222,.16),transparent 26%),radial-gradient(ellipse at 50% 82%,rgba(49,109,214,.08),transparent 38%)!important}
body.contextual-ready #hakhamCore:before{display:none!important}
body.contextual-ready #hakhamCore .core-title{display:none!important}
body.contextual-ready #hakhamCore .avatar-shell{width:min(850px,96vw)!important;height:clamp(570px,72vh,760px)!important;margin:0 auto!important;overflow:visible!important}
body.contextual-ready #hakhamCore .avatar{height:clamp(545px,69vh,735px)!important;max-height:none!important;max-width:98vw!important;object-fit:contain;object-position:center bottom}
body.contextual-ready #hakhamCore .orbit,body.contextual-ready #hakhamCore .energy-disc{display:none!important}
body.contextual-ready #hakhamCore .state{display:none!important}
body.contextual-ready #hakhamCore .synth{position:absolute!important;width:1px!important;height:1px!important;overflow:hidden!important;opacity:0!important;pointer-events:none!important;left:-9999px!important;top:auto!important}
body.contextual-ready #chatPanel{position:fixed!important;z-index:110;left:50%;bottom:14px;transform:translateX(-50%);width:min(980px,calc(100vw - 26px));min-height:0!important;margin:0!important;padding:0!important;border:0!important;border-radius:18px!important;background:transparent!important;box-shadow:none!important;backdrop-filter:none!important;overflow:visible!important;pointer-events:none}
body.contextual-ready #chatPanel:before{display:none!important}
body.contextual-ready #chatPanel .chat-head,body.contextual-ready #chatPanel .chatlog,body.contextual-ready #chatPanel .wabar,body.contextual-ready #chatPanel .visionbar{display:none!important}
body.contextual-ready #chatPanel .compose{pointer-events:auto;display:grid!important;grid-template-columns:minmax(0,1fr) 52px 118px!important;gap:8px!important;padding:9px!important;border:1px solid rgba(37,220,255,.24);border-radius:17px;background:rgba(2,12,23,.84);backdrop-filter:blur(22px) saturate(125%);box-shadow:0 16px 56px rgba(0,0,0,.42),inset 0 0 28px rgba(37,220,255,.025)}
body.contextual-ready #chatPanel .compose textarea{grid-column:1!important;grid-row:1!important;min-height:52px!important;max-height:130px!important;padding:14px 15px!important;border-radius:12px!important;background:rgba(4,23,39,.72)!important;font-size:15px!important;resize:none}
body.contextual-ready #chatPanel #chatMic{grid-column:2!important;grid-row:1!important;min-width:52px!important;min-height:52px!important;border-radius:12px!important}
body.contextual-ready #chatPanel #sendBtn{grid-column:3!important;grid-row:1!important;min-height:52px!important;border-radius:12px!important}
body.contextual-ready .footer{display:none!important}

.context-workspace{position:fixed;z-index:82;inset:72px 10px 88px;pointer-events:none;overflow:visible}
.context-window{--accent:#25dcff;position:absolute;width:min(410px,calc(100vw - 34px));height:min(520px,68vh);min-width:310px;min-height:220px;display:flex;flex-direction:column;overflow:hidden;border:1px solid color-mix(in srgb,var(--accent) 42%,transparent);border-radius:17px;background:linear-gradient(150deg,rgba(5,24,42,.94),rgba(1,8,17,.93));backdrop-filter:blur(24px) saturate(130%);box-shadow:var(--cw-shadow),inset 0 0 48px color-mix(in srgb,var(--accent) 5%,transparent);pointer-events:auto;animation:cwOpen .24s cubic-bezier(.2,.8,.2,1);resize:both}
@keyframes cwOpen{from{opacity:0;transform:translateY(18px) scale(.975)}to{opacity:1;transform:none}}
.context-window[data-kind="instagram"]{--accent:#ff5e9d}.context-window[data-kind="whatsapp"]{--accent:#32e09a}.context-window[data-kind="research"]{--accent:#62b7ff}.context-window[data-kind="drive"]{--accent:#f4c45b}.context-window[data-kind="github"]{--accent:#b590ff}.context-window[data-kind="commercial"]{--accent:#25dcff}.context-window[data-kind="email"]{--accent:#ff9c69}.context-window[data-kind="webcam"]{--accent:#9a70ff}
.context-window.minimized{display:none}
.cw-head{height:48px;display:flex;align-items:center;gap:9px;padding:0 10px 0 13px;border-bottom:1px solid color-mix(in srgb,var(--accent) 24%,transparent);background:linear-gradient(90deg,color-mix(in srgb,var(--accent) 8%,transparent),transparent);cursor:move;user-select:none}
.cw-icon{width:26px;height:26px;border:1px solid color-mix(in srgb,var(--accent) 48%,transparent);border-radius:8px;display:grid;place-items:center;color:var(--accent);box-shadow:0 0 18px color-mix(in srgb,var(--accent) 17%,transparent)}
.cw-title{min-width:0;flex:1}.cw-title b{display:block;font-size:12px;letter-spacing:.09em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.cw-title small{display:block;color:#7799ac;font-size:10px;letter-spacing:.05em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.cw-status{display:inline-flex;align-items:center;gap:5px;font-size:9px;font-weight:850;letter-spacing:.08em;color:var(--accent)}.cw-status:before{content:"";width:6px;height:6px;border-radius:50%;background:var(--accent);box-shadow:0 0 10px var(--accent)}
.cw-btn{width:28px;height:28px;border:1px solid rgba(140,186,210,.18);border-radius:8px;background:rgba(7,25,40,.62);color:#94afbf;cursor:pointer}.cw-btn:hover{border-color:color-mix(in srgb,var(--accent) 50%,transparent);color:#fff}
.cw-body{flex:1;overflow:auto;padding:13px 14px 16px;color:#d9eef8;font-size:13px;line-height:1.52}.cw-query{padding:9px 10px;border:1px solid rgba(111,166,194,.16);border-radius:10px;background:rgba(2,13,24,.55);color:#92b1c1;margin-bottom:11px}.cw-section{margin-top:11px;padding-top:10px;border-top:1px solid rgba(79,132,158,.16)}.cw-section-title{font-size:10px;font-weight:900;letter-spacing:.10em;color:var(--accent);margin-bottom:7px}.cw-answer{white-space:pre-wrap;overflow-wrap:anywhere}.cw-loading{display:flex;align-items:center;gap:9px;color:#88a7b8}.cw-spinner{width:16px;height:16px;border:2px solid rgba(120,180,205,.2);border-top-color:var(--accent);border-radius:50%;animation:cwSpin .8s linear infinite}@keyframes cwSpin{to{transform:rotate(360deg)}}
.cw-profile{display:grid;grid-template-columns:58px minmax(0,1fr);gap:11px;align-items:center}.cw-profile img{width:58px;height:58px;border-radius:50%;object-fit:cover;border:1px solid color-mix(in srgb,var(--accent) 40%,transparent);background:#041321}.cw-profile b{font-size:14px}.cw-profile p{margin:4px 0 0;color:#9bb6c5;font-size:12px}.cw-metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-top:11px}.cw-metric{padding:8px 6px;text-align:center;border:1px solid rgba(94,154,182,.14);border-radius:9px;background:rgba(3,17,29,.48)}.cw-metric b{display:block;color:#fff;font-size:13px}.cw-metric span{font-size:9px;color:#7896a7;letter-spacing:.05em}.cw-media{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px;margin-top:9px}.cw-media a{display:block;min-width:0;text-decoration:none;padding:8px;border:1px solid rgba(100,157,183,.14);border-radius:9px;background:rgba(3,17,29,.48);color:#cceafa}.cw-media b{display:block;font-size:10px;color:var(--accent)}.cw-media span{display:block;font-size:10px;color:#819eae;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:3px}
.context-minibar{position:fixed;z-index:105;left:14px;bottom:18px;display:flex;gap:6px;max-width:calc(50vw - 510px);pointer-events:auto}.context-tab{height:38px;max-width:180px;border:1px solid rgba(37,220,255,.22);border-radius:10px;background:rgba(2,15,27,.88);color:#a9c9d8;padding:0 10px;cursor:pointer;font-size:10px;letter-spacing:.05em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.hakham-caption{position:fixed;z-index:79;left:50%;bottom:92px;transform:translateX(-50%);width:min(720px,calc(100vw - 36px));padding:8px 13px;text-align:center;color:#b8dbe9;font-size:12px;line-height:1.45;opacity:0;transition:opacity .22s;pointer-events:none;text-shadow:0 2px 10px #000}.hakham-caption.show{opacity:.88}

@media(max-width:900px){
 body.contextual-ready{overflow:auto}
 body.contextual-ready .topbar{grid-template-columns:1fr auto!important;position:fixed;width:100%;min-height:58px;padding:7px 9px}
 body.contextual-ready .brand-divider,body.contextual-ready .sercomtec,body.contextual-ready .ser-fallback{display:none!important}
 body.contextual-ready .hakham-brand small{display:none}
 body.contextual-ready .topright .mode-group{display:none}
 body.contextual-ready .engine{max-width:124px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
 body.contextual-ready .page{padding-top:58px;min-height:100vh}
 body.contextual-ready .stage{min-height:calc(100vh - 58px)}
 body.contextual-ready #hakhamCore{min-height:calc(100vh - 58px)!important;padding-bottom:102px!important}
 body.contextual-ready #hakhamCore .avatar-shell{height:clamp(420px,66vh,610px)!important}
 body.contextual-ready #hakhamCore .avatar{height:clamp(400px,63vh,585px)!important}
 .context-workspace{inset:62px 7px 90px}
 .context-window{position:fixed!important;left:7px!important;right:7px!important;top:auto!important;bottom:88px!important;width:auto!important;height:min(58vh,520px)!important;min-width:0;min-height:210px;resize:none;border-radius:16px}
 .cw-head{cursor:default}.cw-media{grid-template-columns:1fr 1fr}
 .context-minibar{left:8px;bottom:82px;max-width:calc(100vw - 16px);overflow:auto}
 .hakham-caption{bottom:83px}
 body.contextual-ready #chatPanel{bottom:8px;width:calc(100vw - 14px)}
 body.contextual-ready #chatPanel .compose{grid-template-columns:minmax(0,1fr) 48px!important;padding:7px!important}
 body.contextual-ready #chatPanel .compose textarea{grid-column:1/-1!important;grid-row:1!important;min-height:48px!important}
 body.contextual-ready #chatPanel #chatMic{grid-column:2!important;grid-row:2!important;min-width:48px!important;min-height:46px!important}
 body.contextual-ready #chatPanel #sendBtn{grid-column:1!important;grid-row:2!important;min-height:46px!important}
}
@media(max-width:520px){.cw-media{grid-template-columns:1fr}.cw-metrics{grid-template-columns:repeat(3,1fr)}body.contextual-ready #hakhamCore .avatar-shell{height:410px!important}body.contextual-ready #hakhamCore .avatar{height:395px!important}}
</style>
"""

CONTEXTUAL_SHELL = r"""
<div class="context-workspace" id="contextWorkspace" aria-live="polite"></div>
<div class="context-minibar" id="contextMinibar"></div>
<div class="hakham-caption" id="hakhamCaption"></div>
"""

CONTEXTUAL_SCRIPT = r"""
<script id="hakham-v19-contextual-workspace-js">
(function(){
  const workspace=document.querySelector('#contextWorkspace');
  const minibar=document.querySelector('#contextMinibar');
  const caption=document.querySelector('#hakhamCaption');
  const windows=new Map();
  let sequence=0;
  let activeWindow=null;

  function cwEsc(value){return String(value??'').replace(/[&<>"']/g,function(m){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]})}
  function cleanText(value){return String(value||'').replace(/\s+/g,' ').trim()}
  function usernameFrom(text){const m=String(text||'').match(/@([A-Za-z0-9._]{2,30})/);return m?m[1]:''}
  function latestOpen(kind){return Array.from(windows.values()).reverse().find(function(w){return !kind||w.dataset.kind===kind})||null}

  function detectIntent(text){
    const low=String(text||'').toLocaleLowerCase('pt-BR');
    if(/instagram|@[a-z0-9._]{2,30}/i.test(text))return{kind:'instagram',icon:'◎',title:'INSTAGRAM DIRECT',detail:usernameFrom(text)?'@'+usernameFrom(text):'ANÁLISE DE PERFIL'};
    if(/whatsapp|whats\b|mensagem para|mande uma mensagem|envie uma mensagem/i.test(text))return{kind:'whatsapp',icon:'◉',title:'WHATSAPP',detail:'CENTRAL DE AÇÃO'};
    if(/\bdrive\b|google drive/i.test(text))return{kind:'drive',icon:'◇',title:'GOOGLE DRIVE',detail:'SER PROJECT VAULT'};
    if(/github|reposit[oó]rio/i.test(text))return{kind:'github',icon:'⌘',title:'GITHUB',detail:'CÓDIGO // SOMENTE LEITURA'};
    if(/orçamento|orcamento|proposta|banner|placa|adesivo|painel/i.test(text))return{kind:'commercial',icon:'▣',title:'COMMERCIAL CORE',detail:'ORÇAMENTO // SER'};
    if(/webcam|c[aâ]mera/i.test(text))return{kind:'webcam',icon:'◈',title:'VISÃO AO VIVO',detail:'WEBCAM // SEM ÁUDIO'};
    if(/e-mail|email/i.test(text))return{kind:'email',icon:'✉',title:'E-MAIL',detail:'AÇÃO EXTERNA'};
    if(/not[ií]cia|esporte|futebol|copa|pesquise|pesquisa|buscar na internet|busque na internet|o que aconteceu hoje|hoje no mundo/i.test(text))return{kind:'research',icon:'⌕',title:'LIVE RESEARCH',detail:'PESQUISA ATUAL'};
    if(/^(pode enviar|pode mandar|aprovo|aprovado|confirma|confirmo)/i.test(cleanText(text))){
      const pending=latestOpen('commercial')||latestOpen('whatsapp')||latestOpen('email');
      if(pending)return{kind:pending.dataset.kind,icon:pending.dataset.icon||'◉',title:pending.dataset.title||'AÇÃO',detail:'CONFIRMAÇÃO'};
    }
    return null;
  }

  function positionWindow(win){
    const index=sequence++%4;
    const desktop=window.innerWidth>900;
    if(!desktop)return;
    win.style.top=(34+(index%2)*72)+'px';
    if(index%2===0){win.style.left=(14+Math.floor(index/2)*28)+'px';win.style.right='auto'}
    else{win.style.right=(14+Math.floor(index/2)*28)+'px';win.style.left='auto'}
  }

  function makeDraggable(win,head){
    let moving=false,dx=0,dy=0;
    head.addEventListener('pointerdown',function(event){
      if(window.innerWidth<=900||event.target.closest('button'))return;
      const rect=win.getBoundingClientRect();moving=true;dx=event.clientX-rect.left;dy=event.clientY-rect.top;
      win.style.left=rect.left+'px';win.style.top=rect.top+'px';win.style.right='auto';head.setPointerCapture(event.pointerId);
    });
    head.addEventListener('pointermove',function(event){if(!moving)return;const maxX=window.innerWidth-win.offsetWidth-8,maxY=window.innerHeight-win.offsetHeight-84;win.style.left=Math.max(8,Math.min(maxX,event.clientX-dx))+'px';win.style.top=Math.max(70,Math.min(maxY,event.clientY-dy))+'px'});
    head.addEventListener('pointerup',function(event){moving=false;try{head.releasePointerCapture(event.pointerId)}catch(e){}});
  }

  function minimize(win){
    win.classList.add('minimized');
    let tab=minibar.querySelector('[data-restore="'+win.id+'"]');
    if(!tab){tab=document.createElement('button');tab.className='context-tab';tab.dataset.restore=win.id;tab.textContent=(win.dataset.icon||'◉')+' '+(win.dataset.title||'JANELA');tab.onclick=function(){win.classList.remove('minimized');tab.remove();activeWindow=win};minibar.appendChild(tab)}
  }
  function closeWindow(win){const tab=minibar.querySelector('[data-restore="'+win.id+'"]');if(tab)tab.remove();windows.delete(win.dataset.kind);win.remove();if(activeWindow===win)activeWindow=null}

  function ensureWindow(spec,query){
    let win=windows.get(spec.kind);
    if(win){win.classList.remove('minimized');const tab=minibar.querySelector('[data-restore="'+win.id+'"]');if(tab)tab.remove();win.querySelector('.cw-query').textContent=query;win.querySelector('.cw-status').textContent='PROCESSANDO';win.querySelector('.cw-answer').textContent='';activeWindow=win;return win}
    win=document.createElement('section');
    win.className='context-window';win.id='cw-'+spec.kind+'-'+Date.now();win.dataset.kind=spec.kind;win.dataset.icon=spec.icon;win.dataset.title=spec.title;
    win.innerHTML='<header class="cw-head"><div class="cw-icon">'+cwEsc(spec.icon)+'</div><div class="cw-title"><b>'+cwEsc(spec.title)+'</b><small>'+cwEsc(spec.detail)+'</small></div><span class="cw-status">PROCESSANDO</span><button class="cw-btn" data-min title="Minimizar">−</button><button class="cw-btn" data-close title="Fechar">×</button></header><div class="cw-body"><div class="cw-query"></div><div class="cw-data"><div class="cw-loading"><span class="cw-spinner"></span><span>Preparando contexto...</span></div></div><div class="cw-section"><div class="cw-section-title">HAKHAM // ANÁLISE</div><div class="cw-answer"></div></div></div>';
    win.querySelector('.cw-query').textContent=query;
    workspace.appendChild(win);positionWindow(win);makeDraggable(win,win.querySelector('.cw-head'));
    win.querySelector('[data-min]').onclick=function(){minimize(win)};win.querySelector('[data-close]').onclick=function(){closeWindow(win)};
    windows.set(spec.kind,win);activeWindow=win;return win
  }

  function setWindowData(win,html){const data=win.querySelector('.cw-data');if(data)data.innerHTML=html}
  function setWindowAnswer(win,text){const answer=win.querySelector('.cw-answer');if(answer)answer.textContent=text||'';const status=win.querySelector('.cw-status');if(status)status.textContent='PRONTO'}
  function setWindowError(win,text){setWindowData(win,'<div class="cw-answer">'+cwEsc(text)+'</div>');const status=win.querySelector('.cw-status');if(status)status.textContent='ATENÇÃO'}

  async function hydrateInstagram(text,win){
    const username=usernameFrom(text);if(!username){setWindowData(win,'<div class="cw-answer">Informe o @usuário para carregar dados do Instagram.</div>');return}
    setWindowData(win,'<div class="cw-loading"><span class="cw-spinner"></span><span>Consultando @'+cwEsc(username)+' via Instagram Direct...</span></div>');
    try{
      const r=await fetch('/api/tools/execute',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({tool_id:'instagram.analyze',arguments:{username:username,media_limit:8},approved:false})});
      let d={};try{d=await r.json()}catch(e){}
      if(!r.ok)throw new Error(d.detail||('HTTP '+r.status));
      const p=d.profile||{},media=Array.isArray(d.media)?d.media:[];
      if(d.source==='public_web'){setWindowData(win,'<div class="cw-answer">Perfil não autenticado no Infinity. Hakham está usando pesquisa pública para @'+cwEsc(username)+'.</div>');return}
      const img=p.profile_picture_url?'<img src="'+cwEsc(p.profile_picture_url)+'" alt="Perfil">':'<div style="width:58px;height:58px;border-radius:50%;border:1px solid rgba(255,94,157,.35);display:grid;place-items:center">◎</div>';
      const metrics='<div class="cw-metrics"><div class="cw-metric"><b>'+cwEsc(p.followers_count??'—')+'</b><span>SEGUIDORES</span></div><div class="cw-metric"><b>'+cwEsc(p.follows_count??'—')+'</b><span>SEGUINDO</span></div><div class="cw-metric"><b>'+cwEsc(p.media_count??'—')+'</b><span>MÍDIAS</span></div></div>';
      const cards=media.slice(0,8).map(function(m){const label=cleanText(m.caption||m.media_type||'Publicação').slice(0,58);return '<a href="'+cwEsc(m.permalink||'#')+'" target="_blank" rel="noopener"><b>'+cwEsc(m.media_type||'POST')+'</b><span>'+cwEsc(label)+'</span></a>'}).join('');
      setWindowData(win,'<div class="cw-profile">'+img+'<div><b>@'+cwEsc(p.username||username)+'</b><p>'+cwEsc(p.name||'')+'</p><p>'+cwEsc(p.biography||'Sem bio retornada pela API')+'</p></div></div>'+metrics+(cards?'<div class="cw-section"><div class="cw-section-title">MÍDIA RECENTE</div><div class="cw-media">'+cards+'</div></div>':''));
    }catch(error){setWindowError(win,'Instagram Direct: '+(error.message||error))}
  }

  function prepareWindow(text){const spec=detectIntent(text);if(!spec)return null;const win=ensureWindow(spec,text);if(spec.kind==='instagram')hydrateInstagram(text,win);else setWindowData(win,'<div class="cw-loading"><span class="cw-spinner"></span><span>Hakham está processando esta missão...</span></div>');return win}

  function lastHakhamAnswer(){const bubbles=Array.from(document.querySelectorAll('#chatLog .bubble'));for(let i=bubbles.length-1;i>=0;i--){if(!bubbles[i].classList.contains('user')){const clone=bubbles[i].cloneNode(true);const strong=clone.querySelector('strong');if(strong)strong.remove();return cleanText(clone.textContent)}}return''}
  function showCaption(text){if(!caption||!text)return;caption.textContent=text.length>260?text.slice(0,257)+'…':text;caption.classList.add('show');clearTimeout(caption._hide);caption._hide=setTimeout(function(){caption.classList.remove('show')},9000)}

  function installContextualSend(){
    if(typeof window.sendChat!=='function'&&typeof sendChat!=='function')return;
    const baseSend=typeof window.sendChat==='function'?window.sendChat:sendChat;
    async function contextualSend(){
      const input=document.querySelector('#chatInput');const text=(input&&input.value||'').trim();if(!text)return;
      const win=prepareWindow(text);activeWindow=win||activeWindow;
      try{await baseSend()}finally{const answer=lastHakhamAnswer();if(win&&answer)setWindowAnswer(win,answer);if(answer)showCaption(answer)}
    }
    try{window.sendChat=contextualSend;sendChat=contextualSend}catch(e){window.sendChat=contextualSend}
    const button=document.querySelector('#sendBtn');if(button)button.onclick=contextualSend;
  }

  function contextualizeToolClicks(){document.addEventListener('click',function(event){const tool=event.target.closest&&event.target.closest('[data-tool]');if(!tool)return;const id=tool.dataset.tool||'';const map={instagram:{kind:'instagram',icon:'◎',title:'INSTAGRAM DIRECT',detail:'ANÁLISE DE PERFIL'},drive:{kind:'drive',icon:'◇',title:'GOOGLE DRIVE',detail:'SER PROJECT VAULT'},github:{kind:'github',icon:'⌘',title:'GITHUB',detail:'CÓDIGO // SOMENTE LEITURA'},whatsapp:{kind:'whatsapp',icon:'◉',title:'WHATSAPP',detail:'CENTRAL DE AÇÃO'},email:{kind:'email',icon:'✉',title:'E-MAIL',detail:'AÇÃO EXTERNA'}};const key=Object.keys(map).find(function(k){return id.indexOf(k)===0});if(key)ensureWindow(map[key],tool.textContent.trim())},true)}

  function install(){document.body.classList.add('contextual-ready');installContextualSend();contextualizeToolClicks();const input=document.querySelector('#chatInput');if(input)input.placeholder='Fale com Hakham ou digite uma missão...';}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install,{once:true});else install();
})();
</script>
"""


def _enhance(html: str) -> str:
    html = html.replace("Orbit Command v0.17 Instagram Direct", "Orbit Command v0.19 Contextual Workspace")
    html = html.replace("ORBIT COMMAND // v0.17 INSTAGRAM DIRECT", "ORBIT COMMAND // v0.19 CONTEXTUAL WORKSPACE")
    html = html.replace("HAKHAM INFINITY ∞ v0.17 // SER Comtec", "HAKHAM INFINITY ∞ v0.19 // SER Comtec")
    html = html.replace("</head>", CONTEXTUAL_UI + "\n</head>")
    html = html.replace("</body>", CONTEXTUAL_SHELL + "\n" + CONTEXTUAL_SCRIPT + "\n</body>")
    return html


_stable_web = previous._stable_web
_stable_web.CONTROL_CENTER_HTML = _enhance(_stable_web.CONTROL_CENTER_HTML)
CONTROL_CENTER_HTML = _stable_web.CONTROL_CENTER_HTML


def main() -> None:
    import uvicorn

    uvicorn.run("hakham.web_v19:app", host="127.0.0.1", port=8765, reload=False)


if __name__ == "__main__":
    main()
