from __future__ import annotations

from . import web_v19_3 as previous


app = previous.app

FUSION_UI = r"""
<style id="hakham-v19-4-reactor-fusion">
/* Reactor Fusion: cover the infinity already present in Hakham's official art. */
body.contextual-ready #hakhamCore .avatar-shell{overflow:visible!important}
.infinity-reactor{
  width:min(99%,840px)!important;
  max-width:none!important;
  height:auto!important;
  aspect-ratio:360/190!important;
  left:50%!important;
  bottom:5.4%!important;
  z-index:7!important;
  opacity:.99!important;
  mix-blend-mode:screen!important;
  transform:translateX(-50%) scale(calc(.99 + var(--ir-energy)*.038))!important;
  transform-origin:50% 50%!important;
  filter:drop-shadow(0 0 calc(14px + var(--ir-energy)*30px) rgba(37,220,255,.72)) drop-shadow(0 0 calc(30px + var(--ir-energy)*42px) rgba(29,133,255,.30))!important;
}
.infinity-reactor svg{overflow:visible!important}
.infinity-reactor .ir-shadow{display:none!important}
.infinity-reactor .ir-track{
  stroke:rgba(105,222,255,.72)!important;
  stroke-width:7.2!important;
  opacity:.72!important;
  filter:drop-shadow(0 0 7px rgba(37,220,255,.86))!important;
}
.infinity-reactor .ir-halo{
  stroke:#2ddfff!important;
  stroke-width:18!important;
  opacity:calc(.16 + var(--ir-energy)*.31)!important;
  filter:blur(6px)!important;
}
.infinity-reactor .ir-flow{
  stroke:#b9f8ff!important;
  stroke-width:6.8!important;
  stroke-dasharray:7 10!important;
  opacity:.98!important;
  filter:drop-shadow(0 0 5px #25dcff) drop-shadow(0 0 10px rgba(37,220,255,.82))!important;
}
.infinity-reactor .ir-pulse{
  stroke:#54e9ff!important;
  stroke-width:4.4!important;
  stroke-dasharray:2 7!important;
  opacity:calc(.48 + var(--ir-energy)*.48)!important;
  filter:drop-shadow(0 0 5px #25dcff)!important;
}
.infinity-reactor .ir-node{fill:#bffbff!important;opacity:.72!important;filter:drop-shadow(0 0 8px #25dcff)!important}
.infinity-reactor .ir-center{fill:#fff!important;opacity:.94!important;filter:drop-shadow(0 0 7px #fff) drop-shadow(0 0 18px #25dcff)!important}
.infinity-reactor .ir-state{display:none!important}
#hakhamCore[data-state="idle"] .ir-flow{animation-duration:5.8s!important;opacity:.78!important}
#hakhamCore[data-state="listening"] .ir-track,#hakhamCore[data-state="listening"] .ir-halo,#hakhamCore[data-state="listening"] .ir-flow{stroke:#52ffd1!important}
#hakhamCore[data-state="listening"] .ir-flow{animation-duration:1.15s!important;stroke-dasharray:5 7!important}
#hakhamCore[data-state="thinking"] .ir-track,#hakhamCore[data-state="thinking"] .ir-halo,#hakhamCore[data-state="thinking"] .ir-flow{stroke:#aa85ff!important}
#hakhamCore[data-state="thinking"] .ir-flow{animation-duration:1.42s!important;stroke-dasharray:4 6!important}
#hakhamCore[data-state="speaking"] .ir-flow{animation-duration:.65s!important;stroke-width:calc(6.8px + var(--ir-energy)*6px)!important;stroke-dasharray:3 5!important}
#hakhamCore[data-state="speaking"] .ir-halo{stroke-width:calc(18px + var(--ir-energy)*15px)!important;opacity:calc(.22 + var(--ir-energy)*.42)!important}
#hakhamCore[data-state="executing"] .ir-flow{stroke:#ffd27a!important;animation-duration:.85s!important;stroke-dasharray:8 5!important}
#hakhamCore[data-state="executing"] .ir-pulse{stroke:#25dcff!important}

/* Image sending in the clean hero composer. */
body.contextual-ready #chatPanel .compose{grid-template-columns:minmax(0,1fr) 52px 52px 118px!important}
body.contextual-ready #chatPanel #contextImageBtn{grid-column:2!important;grid-row:1!important}
body.contextual-ready #chatPanel #chatMic{grid-column:3!important;grid-row:1!important}
body.contextual-ready #chatPanel #sendBtn{grid-column:4!important;grid-row:1!important}
.context-image-btn{min-width:52px!important;min-height:52px!important;border:1px solid rgba(37,220,255,.36)!important;border-radius:12px!important;background:rgba(6,38,58,.82)!important;color:#c8f7ff!important;font-size:18px!important;cursor:pointer!important;box-shadow:inset 0 0 20px rgba(37,220,255,.04)!important}
.context-image-btn:hover{border-color:#56e7ff!important;box-shadow:0 0 20px rgba(37,220,255,.13),inset 0 0 20px rgba(37,220,255,.06)!important}
body.image-drop-ready #chatPanel .compose{border-color:rgba(37,220,255,.72)!important;box-shadow:0 0 38px rgba(37,220,255,.16)!important}
.context-window[data-kind="image"]{--accent:#47e7ff;width:min(470px,calc(100vw - 34px));height:min(570px,72vh)}
.cw-image-preview{width:100%;max-height:300px;display:block;object-fit:contain;border:1px solid rgba(71,231,255,.24);border-radius:12px;background:rgba(0,6,13,.72);box-shadow:inset 0 0 35px rgba(37,220,255,.04)}
.cw-image-meta{display:flex;justify-content:space-between;gap:9px;margin-top:8px;color:#83a8b9;font-size:10px}.cw-image-meta b{color:#dffaff;font-weight:750;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.cw-image-hint{margin-top:9px;padding:8px 9px;border:1px solid rgba(71,231,255,.15);border-radius:9px;background:rgba(3,18,31,.48);color:#8fadb9;font-size:10px}

@media(max-width:900px){
 .infinity-reactor{width:min(99%,600px)!important;bottom:5.8%!important}
 body.contextual-ready #chatPanel .compose{grid-template-columns:minmax(0,1fr) 48px 48px!important}
 body.contextual-ready #chatPanel .compose textarea{grid-column:1/-1!important;grid-row:1!important}
 body.contextual-ready #chatPanel #sendBtn{grid-column:1!important;grid-row:2!important}
 body.contextual-ready #chatPanel #contextImageBtn{grid-column:2!important;grid-row:2!important;min-width:48px!important;min-height:46px!important}
 body.contextual-ready #chatPanel #chatMic{grid-column:3!important;grid-row:2!important;min-width:48px!important;min-height:46px!important}
}
@media(max-width:520px){.infinity-reactor{width:101%!important;bottom:6.3%!important}.context-window[data-kind="image"]{height:min(61vh,510px)!important}}
</style>
"""

FUSION_SCRIPT = r"""
<script id="hakham-v19-4-reactor-fusion-js">
(function(){
  const compose=document.querySelector('#chatPanel .compose');
  const input=document.querySelector('#chatInput');
  const mic=document.querySelector('#chatMic');
  const workspace=document.querySelector('#contextWorkspace');
  if(!compose||!input||!workspace)return;

  let fileInput=document.querySelector('#contextImageFile');
  if(!fileInput){
    fileInput=document.createElement('input');
    fileInput.id='contextImageFile';fileInput.type='file';fileInput.hidden=true;
    fileInput.accept='image/png,image/jpeg,image/webp,image/gif';
    compose.appendChild(fileInput);
  }
  let imageBtn=document.querySelector('#contextImageBtn');
  if(!imageBtn){
    imageBtn=document.createElement('button');imageBtn.id='contextImageBtn';imageBtn.type='button';imageBtn.className='context-image-btn';
    imageBtn.title='Enviar imagem para Hakham';imageBtn.setAttribute('aria-label','Enviar imagem para Hakham');imageBtn.textContent='▧';
    if(mic)mic.insertAdjacentElement('beforebegin',imageBtn);else compose.appendChild(imageBtn);
  }

  function esc(value){return String(value??'').replace(/[&<>"']/g,function(m){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]})}
  function fmtBytes(n){if(n<1024)return n+' B';if(n<1024*1024)return (n/1024).toFixed(1)+' KB';return (n/(1024*1024)).toFixed(1)+' MB'}
  function toDataURL(file){return new Promise(function(resolve,reject){const r=new FileReader();r.onload=function(){resolve(String(r.result))};r.onerror=function(){reject(r.error||new Error('Falha ao ler a imagem'))};r.readAsDataURL(file)})}

  function place(win){if(window.innerWidth<=900)return;win.style.left='18px';win.style.right='auto';win.style.top='44px'}
  function makeDraggable(win,head){let moving=false,dx=0,dy=0;head.addEventListener('pointerdown',function(event){if(window.innerWidth<=900||event.target.closest('button'))return;const rect=win.getBoundingClientRect();moving=true;dx=event.clientX-rect.left;dy=event.clientY-rect.top;win.style.left=rect.left+'px';win.style.top=rect.top+'px';win.style.right='auto';head.setPointerCapture(event.pointerId)});head.addEventListener('pointermove',function(event){if(!moving)return;const maxX=window.innerWidth-win.offsetWidth-8,maxY=window.innerHeight-win.offsetHeight-88;win.style.left=Math.max(8,Math.min(maxX,event.clientX-dx))+'px';win.style.top=Math.max(70,Math.min(maxY,event.clientY-dy))+'px'});head.addEventListener('pointerup',function(event){moving=false;try{head.releasePointerCapture(event.pointerId)}catch(e){}})}

  function closeImageWindow(win){const tab=document.querySelector('[data-image-restore="'+win.id+'"]');if(tab)tab.remove();if(win&&win.isConnected)win.remove()}
  function minimizeImageWindow(win){win.classList.add('minimized');const bar=document.querySelector('#contextMinibar');if(!bar)return;let tab=bar.querySelector('[data-image-restore="'+win.id+'"]');if(!tab){tab=document.createElement('button');tab.className='context-tab';tab.dataset.imageRestore=win.id;tab.textContent='▧ VISÃO HAKHAM';tab.onclick=function(){win.classList.remove('minimized');tab.remove()};bar.appendChild(tab)}}

  function openImageWindow(file,dataUrl,context){
    let win=workspace.querySelector('.context-window[data-kind="image"]');
    if(!win){
      win=document.createElement('section');win.className='context-window';win.dataset.kind='image';win.id='cw-image-'+Date.now();
      win.innerHTML='<header class="cw-head"><div class="cw-icon">▧</div><div class="cw-title"><b>VISÃO HAKHAM</b><small>IMAGEM // MEMÓRIA VISUAL</small></div><span class="cw-status">CARREGANDO</span><button class="cw-btn" data-min title="Minimizar">−</button><button class="cw-btn" data-close title="Fechar">×</button></header><div class="cw-body"><div class="cw-query"></div><div class="cw-data"></div><div class="cw-section"><div class="cw-section-title">HAKHAM // LEITURA VISUAL</div><div class="cw-answer"></div></div></div>';
      workspace.appendChild(win);place(win);makeDraggable(win,win.querySelector('.cw-head'));win.querySelector('[data-close]').onclick=function(){closeImageWindow(win)};win.querySelector('[data-min]').onclick=function(){minimizeImageWindow(win)};
    }
    win.classList.remove('minimized');
    const tab=document.querySelector('[data-image-restore="'+win.id+'"]');if(tab)tab.remove();
    win.querySelector('.cw-query').textContent=context||'Analise esta imagem, Hakham.';
    win.querySelector('.cw-status').textContent='ANALISANDO';
    win.querySelector('.cw-answer').textContent='';
    win.querySelector('.cw-data').innerHTML='<img class="cw-image-preview" src="'+esc(dataUrl)+'" alt="Imagem enviada ao Hakham"><div class="cw-image-meta"><b>'+esc(file.name||'imagem')+'</b><span>'+esc(fmtBytes(file.size||0))+'</span></div><div class="cw-image-hint">A imagem entra na memória visual somente após a análise ser concluída.</div>';
    return win;
  }

  function announce(text){
    const caption=document.querySelector('#hakhamCaption');if(caption){caption.textContent=text;caption.classList.add('show');clearTimeout(caption._v194hide);caption._v194hide=setTimeout(function(){caption.classList.remove('show')},8000)}
    try{if(typeof speakHakham==='function'&&text)speakHakham(text)}catch(e){}
  }

  async function processImage(file){
    if(!file)return;
    const allowed=['image/png','image/jpeg','image/webp','image/gif'];
    if(!allowed.includes(String(file.type||'').toLowerCase())){if(typeof toast==='function')toast('Formato de imagem não suportado');return}
    if(file.size>12*1024*1024){if(typeof toast==='function')toast('Imagem maior que 12 MB');return}
    let dataUrl='';
    try{dataUrl=await toDataURL(file)}catch(e){if(typeof toast==='function')toast('Não consegui ler a imagem');return}
    const context=input.value.trim()||'Imagem enviada pelo Ach para análise visual.';
    if(input.value.trim())input.value='';
    const win=openImageWindow(file,dataUrl,context);
    try{if(typeof setState==='function')setState('thinking','ANALISANDO IMAGEM')}catch(e){}
    try{
      const r=await fetch('/api/vision/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({data_url:dataUrl,filename:file.name||'imagem',context:context})});
      let d={};try{d=await r.json()}catch(e){}
      if(!r.ok)throw new Error(d.detail||('HTTP '+r.status));
      const answer=d.answer||(d.item&&d.item.description)||'Imagem analisada e memorizada.';
      win.querySelector('.cw-status').textContent='MEMORIZADA';win.querySelector('.cw-answer').textContent=answer;
      const hint=win.querySelector('.cw-image-hint');if(hint)hint.textContent='✓ Hakham analisou esta imagem e registrou a observação na memória visual.';
      if(typeof toast==='function')toast('Hakham viu a imagem e guardou a memória');announce(answer);
    }catch(e){
      win.querySelector('.cw-status').textContent='ATENÇÃO';win.querySelector('.cw-answer').textContent='Não consegui concluir a análise: '+(e.message||e);
      if(typeof toast==='function')toast('Visão: '+(e.message||e));
    }finally{try{if(typeof setState==='function')setState('idle','PRONTO')}catch(e){}}
  }

  imageBtn.addEventListener('click',function(){fileInput.click()});
  fileInput.addEventListener('change',function(){const file=fileInput.files&&fileInput.files[0];fileInput.value='';processImage(file)});

  compose.addEventListener('dragover',function(event){if(Array.from(event.dataTransfer?.items||[]).some(function(i){return i.kind==='file'&&String(i.type||'').startsWith('image/')})){event.preventDefault();document.body.classList.add('image-drop-ready')}});
  compose.addEventListener('dragleave',function(){document.body.classList.remove('image-drop-ready')});
  compose.addEventListener('drop',function(event){document.body.classList.remove('image-drop-ready');const file=Array.from(event.dataTransfer?.files||[]).find(function(f){return String(f.type||'').startsWith('image/')});if(file){event.preventDefault();processImage(file)}});
  input.addEventListener('paste',function(event){const file=Array.from(event.clipboardData?.files||[]).find(function(f){return String(f.type||'').startsWith('image/')});if(file){event.preventDefault();processImage(file)}});

  /* Specific voice/text command to close the visual card. Generic 'feche o card'
     remains handled by v0.19.3. */
  const previousSend=typeof window.sendChat==='function'?window.sendChat:null;
  async function v194Send(){
    const text=String(input.value||'').trim();
    if(/\b(feche|fecha|fechar|encerre|remova)\b.{0,24}\b(imagem|foto|vis[aã]o)\b/i.test(text)){
      const win=workspace.querySelector('.context-window[data-kind="image"]');input.value='';
      if(win){closeImageWindow(win);announce('Fechando a imagem, Ach.')}else announce('Não há card de imagem aberto, Ach.');
      return;
    }
    if(previousSend)return previousSend();
  }
  window.sendChat=v194Send;try{sendChat=v194Send}catch(e){}
  const send=document.querySelector('#sendBtn');if(send)send.onclick=v194Send;

  /* Remove the never-ending spinner from a research card after the answer arrives. */
  const observer=new MutationObserver(function(){workspace.querySelectorAll('.context-window[data-kind="research"]').forEach(function(win){const status=win.querySelector('.cw-status');const answer=win.querySelector('.cw-answer');const data=win.querySelector('.cw-data');if(status&&answer&&data&&status.textContent==='PRONTO'&&answer.textContent.trim()&&data.querySelector('.cw-loading'))data.innerHTML='<div class="cw-local-row"><b>PESQUISA CONCLUÍDA</b><small>Resultados atuais entregues ao Hakham para síntese.</small></div>'})});
  observer.observe(workspace,{subtree:true,childList:true,characterData:true});
})();
</script>
"""


def _enhance(html: str) -> str:
    html = html.replace("Orbit Command v0.19.3 Context Controls", "Orbit Command v0.19.4 Reactor Fusion")
    html = html.replace("ORBIT COMMAND // v0.19.3 CONTEXT CONTROLS", "ORBIT COMMAND // v0.19.4 REACTOR FUSION")
    html = html.replace("HAKHAM INFINITY ∞ v0.19.3 // SER Comtec", "HAKHAM INFINITY ∞ v0.19.4 // SER Comtec")
    html = html.replace("</head>", FUSION_UI + "\n</head>")
    html = html.replace("</body>", FUSION_SCRIPT + "\n</body>")
    return html


_stable_web = previous._stable_web
_stable_web.CONTROL_CENTER_HTML = _enhance(_stable_web.CONTROL_CENTER_HTML)
CONTROL_CENTER_HTML = _stable_web.CONTROL_CENTER_HTML


def main() -> None:
    import uvicorn

    uvicorn.run("hakham.web_v19_4:app", host="127.0.0.1", port=8765, reload=False)


if __name__ == "__main__":
    main()
