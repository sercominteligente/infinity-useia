from __future__ import annotations

from . import web_v15 as open_core_layer
from .external_integrations import install_external_tool_patch


app = open_core_layer.app
install_external_tool_patch()

INTEGRATION_UI = r"""
<style id="hakham-v16-integrations">
.integration-chip{display:inline-flex;align-items:center;gap:6px;margin-left:6px;padding:4px 9px;border:1px solid rgba(154,112,255,.35);border-radius:999px;background:rgba(32,19,63,.58);color:#cab8ff;font-size:10px;font-weight:800;letter-spacing:.05em;white-space:nowrap}.integration-chip:before{content:"";width:7px;height:7px;border-radius:50%;background:#9a70ff;box-shadow:0 0 11px #9a70ff}
.wa-call-btn{height:40px!important;border-color:rgba(244,183,91,.55)!important;background:rgba(74,49,10,.78)!important;color:#ffe2a9!important}.wa-call-btn:hover{border-color:#ffd084!important}
.camera-btn{border-color:rgba(154,112,255,.55)!important;background:rgba(38,24,73,.72)!important;color:#e9e0ff!important}.camera-live{display:inline-flex;align-items:center;gap:6px;color:#ff8096;font-weight:900;font-size:11px;letter-spacing:.06em}.camera-live:before{content:"";width:8px;height:8px;border-radius:50%;background:#ff647b;box-shadow:0 0 14px #ff647b;animation:cameraBlink .8s ease-in-out infinite alternate}@keyframes cameraBlink{to{opacity:.35}}
.camera-modal{position:fixed;inset:0;z-index:120;display:none;align-items:center;justify-content:center;padding:18px;background:rgba(0,3,9,.78);backdrop-filter:blur(12px)}.camera-modal.open{display:flex}.camera-shell{width:min(860px,96vw);border:1px solid rgba(37,220,255,.35);border-radius:20px;background:linear-gradient(145deg,rgba(4,19,34,.98),rgba(1,8,16,.98));box-shadow:0 30px 90px rgba(0,0,0,.65),0 0 70px rgba(24,173,229,.10) inset;padding:15px}.camera-head{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:10px}.camera-head strong{letter-spacing:.09em}.camera-stage{position:relative;aspect-ratio:16/9;border:1px solid rgba(37,220,255,.24);border-radius:14px;overflow:hidden;background:#000}.camera-stage video{width:100%;height:100%;object-fit:cover;display:block;transform:scaleX(-1)}.camera-stage .scan{position:absolute;left:0;right:0;height:1px;top:12%;background:linear-gradient(90deg,transparent,#25dcff,transparent);box-shadow:0 0 16px #25dcff;animation:cameraScan 3.5s linear infinite;pointer-events:none}@keyframes cameraScan{0%{top:8%}50%{top:92%}100%{top:8%}}.camera-actions{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin-top:11px}.camera-actions button{min-height:44px;border:1px solid rgba(37,220,255,.38);border-radius:10px;background:rgba(8,48,67,.75);color:#e8fbff;font-weight:850;cursor:pointer}.camera-actions button.danger{border-color:rgba(255,100,123,.4);background:rgba(74,18,29,.65);color:#ffb2be}.camera-note{margin-top:9px;color:#819eae;font-size:12px}.camera-note b{color:#ff91a3}.camera-close{border:1px solid rgba(255,100,123,.35);background:rgba(68,16,26,.64);color:#ffb0bc;border-radius:9px;padding:7px 10px;cursor:pointer}
.tool[data-tool="whatsapp.call"],.tool[data-tool="email.send"],.tool[data-tool="webcam.capture"]{box-shadow:inset 0 0 25px rgba(154,112,255,.035)}
@media(max-width:760px){.integration-chip{font-size:9px}.camera-modal{padding:8px}.camera-shell{padding:10px;border-radius:15px}.camera-actions{grid-template-columns:1fr}.wabar{grid-template-columns:1fr!important}.wa-call-btn{width:100%}}
</style>
"""

CAMERA_MODAL = r"""
<div class="camera-modal" id="cameraModal" aria-hidden="true">
  <section class="camera-shell" role="dialog" aria-modal="true" aria-label="Webcam Hakham Infinity">
    <div class="camera-head"><div><strong>HAKHAM VISION // WEBCAM</strong> <span class="camera-live" id="cameraLive">VISÃO AO VIVO</span></div><button class="camera-close" id="cameraClose" type="button">ENCERRAR</button></div>
    <div class="camera-stage"><video id="cameraVideo" autoplay playsinline muted></video><div class="scan"></div></div>
    <div class="camera-actions"><button id="cameraCapture" type="button">📷 CAPTURAR QUADRO PARA HAKHAM</button><button class="danger" id="cameraStop" type="button">■ DESLIGAR CÂMERA</button></div>
    <div class="camera-note">A câmera só permanece ativa enquanto este painel estiver aberto. <b>Áudio não é capturado.</b> O quadro só entra na memória visual quando você tocar em CAPTURAR.</div>
  </section>
</div>
"""

INTEGRATION_SCRIPT = r"""
<script id="hakham-v16-integrations-js">
(function(){
  let cameraStream=null;
  const cameraModal=document.querySelector('#cameraModal');
  const cameraVideo=document.querySelector('#cameraVideo');
  const cameraCapture=document.querySelector('#cameraCapture');
  const cameraStop=document.querySelector('#cameraStop');
  const cameraClose=document.querySelector('#cameraClose');

  function addSystemBubble(role,text){
    if(typeof addBubble==='function'){addBubble(role,text);return}
    const log=document.querySelector('#chatLog');if(!log)return;
    const d=document.createElement('div');d.className='bubble';const s=document.createElement('strong');s.textContent=role;d.appendChild(s);d.appendChild(document.createTextNode(text));log.appendChild(d);log.scrollTop=log.scrollHeight;
  }

  function addVisionBubble(role,text,imgUrl,user){
    const log=document.querySelector('#chatLog');if(!log)return;
    const b=document.createElement('div');b.className='bubble'+(user?' user':'');
    const s=document.createElement('strong');s.textContent=role;b.appendChild(s);
    const t=document.createElement('div');t.textContent=text;b.appendChild(t);
    if(imgUrl){const img=document.createElement('img');img.src=imgUrl;img.className='vision-preview';img.alt='Quadro capturado da webcam';b.appendChild(img)}
    log.appendChild(b);log.scrollTop=log.scrollHeight;
  }

  async function startCamera(){
    if(!navigator.mediaDevices||!navigator.mediaDevices.getUserMedia){
      addSystemBubble('HAKHAM · WEBCAM','Este navegador não disponibiliza acesso à webcam via MediaDevices.');return;
    }
    if(cameraStream){cameraModal?.classList.add('open');cameraModal?.setAttribute('aria-hidden','false');return}
    try{
      if(typeof setState==='function')setState('executing','VISÃO AO VIVO');
      cameraStream=await navigator.mediaDevices.getUserMedia({video:{facingMode:'user',width:{ideal:1280},height:{ideal:720}},audio:false});
      if(cameraVideo){cameraVideo.srcObject=cameraStream;await cameraVideo.play().catch(()=>{});}
      cameraModal?.classList.add('open');cameraModal?.setAttribute('aria-hidden','false');
      document.body.classList.add('webcam-live');
      if(typeof toast==='function')toast('Webcam ativa · áudio desligado');
    }catch(e){
      cameraStream=null;if(typeof setState==='function')setState('idle','EM ESPERA');
      addSystemBubble('HAKHAM · WEBCAM','Não consegui ativar a webcam: '+(e.message||e)+'. Verifique a permissão do navegador.');
    }
  }

  function stopCamera(){
    if(cameraStream){cameraStream.getTracks().forEach(track=>track.stop());cameraStream=null}
    if(cameraVideo)cameraVideo.srcObject=null;
    cameraModal?.classList.remove('open');cameraModal?.setAttribute('aria-hidden','true');
    document.body.classList.remove('webcam-live');
    if(typeof setState==='function')setState('idle','EM ESPERA');
  }

  async function captureCamera(){
    if(!cameraStream||!cameraVideo||!cameraVideo.videoWidth){if(typeof toast==='function')toast('Webcam ainda não está pronta');return}
    const canvas=document.createElement('canvas');
    canvas.width=Math.min(cameraVideo.videoWidth,1600);canvas.height=Math.round(canvas.width*(cameraVideo.videoHeight/cameraVideo.videoWidth));
    const ctx=canvas.getContext('2d');if(!ctx)return;
    ctx.translate(canvas.width,0);ctx.scale(-1,1);ctx.drawImage(cameraVideo,0,0,canvas.width,canvas.height);
    const dataUrl=canvas.toDataURL('image/jpeg',.86);
    const filename='webcam-'+new Date().toISOString().replace(/[:.]/g,'-')+'.jpg';
    addVisionBubble('ACH · WEBCAM',filename,dataUrl,true);
    if(typeof setState==='function')setState('thinking','ANALISANDO WEBCAM');
    try{
      const context=(document.querySelector('#chatInput')?.value||'').trim()||'Quadro capturado da webcam pelo Ach.';
      const r=await fetch('/api/vision/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({data_url:dataUrl,filename:filename,context:context})});
      let d={};try{d=await r.json()}catch(e){}
      if(!r.ok)throw new Error(d.detail||('HTTP '+r.status));
      const answer=d.answer||d.item?.description||'Quadro analisado.';
      addVisionBubble('HAKHAM · WEBCAM',answer,'',false);
      if(typeof speakHakham==='function'&&answer)speakHakham(answer);
      if(typeof toast==='function')toast('Quadro visto e memorizado');
    }catch(e){addSystemBubble('HAKHAM · WEBCAM','Falha ao analisar o quadro: '+e.message)}
    finally{if(typeof setState==='function')setState('idle','EM ESPERA')}
  }

  if(cameraCapture)cameraCapture.addEventListener('click',captureCamera);
  if(cameraStop)cameraStop.addEventListener('click',stopCamera);
  if(cameraClose)cameraClose.addEventListener('click',stopCamera);
  if(cameraModal)cameraModal.addEventListener('click',e=>{if(e.target===cameraModal)stopCamera()});
  document.addEventListener('visibilitychange',()=>{if(document.hidden&&cameraStream)stopCamera()});
  window.addEventListener('beforeunload',stopCamera);

  function installButtons(){
    const visionBar=document.querySelector('.visionbar');
    const visionBtn=document.querySelector('#visionBtn');
    if(visionBar&&visionBtn&&!document.querySelector('#webcamBtn')){
      const btn=document.createElement('button');btn.id='webcamBtn';btn.type='button';btn.className='camera-btn';btn.textContent='📷 WEBCAM';btn.addEventListener('click',startCamera);visionBtn.insertAdjacentElement('afterend',btn);
    }
    const wa=document.querySelector('.wabar');
    const send=document.querySelector('#waSendBtn');
    if(wa&&send&&!document.querySelector('#waCallBtn')){
      const btn=document.createElement('button');btn.id='waCallBtn';btn.type='button';btn.className='wa-call-btn';btn.textContent='☎ LIGAR';send.insertAdjacentElement('afterend',btn);
      btn.addEventListener('click',async()=>{
        const number=(document.querySelector('#waNumber')?.value||'').replace(/\D/g,'');
        if(!number){if(typeof toast==='function')toast('Informe o número com DDI e DDD');return}
        if(!window.confirm('Autorizar HAKHAM Infinity a iniciar uma chamada de áudio pelo WhatsApp para '+number+'?'))return;
        btn.disabled=true;btn.textContent='LIGANDO...';if(typeof setState==='function')setState('executing','CHAMADA WHATSAPP');
        try{
          const r=await fetch('/api/tools/execute',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({tool_id:'whatsapp.call',arguments:{number:number,is_video:false,call_duration:20},approved:true})});
          let d={};try{d=await r.json()}catch(e){}
          if(!r.ok)throw new Error(d.detail||('HTTP '+r.status));
          addSystemBubble('HAKHAM · WHATSAPP','A Evolution aceitou a solicitação de chamada para '+number+'. Isso não confirma que o destinatário atendeu.');
          if(typeof toast==='function')toast('Oferta de chamada enviada');
        }catch(e){addSystemBubble('HAKHAM · WHATSAPP','Não consegui iniciar a chamada: '+e.message);if(typeof toast==='function')toast('Chamada: '+e.message)}
        finally{btn.disabled=false;btn.textContent='☎ LIGAR';if(typeof setState==='function')setState('idle','EM ESPERA')}
      });
    }
  }

  function cameraIntent(text){return /(?:ative|ativar|ligue|abr[ae]|inicie).{0,18}(?:webcam|c[aâ]mera)/i.test(text||'')}
  function cameraStopIntent(text){return /(?:desative|desligue|feche|pare).{0,18}(?:webcam|c[aâ]mera)/i.test(text||'')}
  function interceptCamera(){
    const input=document.querySelector('#chatInput');const text=(input?.value||'').trim();
    if(cameraStopIntent(text)){if(input)input.value='';addSystemBubble('ACH',text);stopCamera();addSystemBubble('HAKHAM','Webcam desligada.');return true}
    if(cameraIntent(text)){if(input)input.value='';addSystemBubble('ACH',text);startCamera();return true}
    return false;
  }

  const sendBtn=document.querySelector('#sendBtn');if(sendBtn)sendBtn.addEventListener('click',e=>{if(interceptCamera()){e.preventDefault();e.stopImmediatePropagation()}},true);
  const input=document.querySelector('#chatInput');if(input)input.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey&&interceptCamera()){e.preventDefault();e.stopImmediatePropagation()}},true);

  document.addEventListener('click',function(event){
    const tile=event.target.closest&&event.target.closest('#toolGrid .tool');if(!tile)return;
    const id=tile.dataset.tool||'';const input=document.querySelector('#chatInput');if(!input)return;
    const prompts={
      'whatsapp.call':'Hakham, faça uma ligação pelo WhatsApp para ',
      'drive.read':'Hakham, procure no nosso Drive ',
      'github.find_repository':'Hakham, abra no GitHub o projeto ',
      'github.tree':'Hakham, abra no GitHub o projeto ',
      'github.read_file':'Hakham, abra no GitHub o projeto ',
      'instagram.analyze':'Hakham, analise o Instagram @',
      'email.send':'Hakham, envie um e-mail para  assunto:  mensagem: '
    };
    if(id==='webcam.capture'){event.preventDefault();event.stopImmediatePropagation();startCamera();return}
    if(prompts[id]){event.preventDefault();event.stopImmediatePropagation();input.value=prompts[id];input.focus();document.querySelector('#chatPanel')?.scrollIntoView({behavior:'smooth'});}
  },true);

  const toolGrid=document.querySelector('#toolGrid');if(toolGrid)new MutationObserver(installButtons).observe(toolGrid,{childList:true,subtree:true});
  installButtons();setTimeout(installButtons,900);setTimeout(installButtons,2200);
})();
</script>
"""


def _enhance(html: str) -> str:
    html = html.replace("Orbit Command v0.15 Open Core", "Orbit Command v0.16 Integration Gateway")
    html = html.replace("ORBIT COMMAND // v0.15 OPEN CORE", "ORBIT COMMAND // v0.16 INTEGRATION GATEWAY")
    html = html.replace("HAKHAM INFINITY ∞ v0.15 // SER Comtec", "HAKHAM INFINITY ∞ v0.16 // SER Comtec")
    html = html.replace("</head>", INTEGRATION_UI + "\n</head>")
    marker = '<span class="commercial-chip">COMMERCIAL CORE</span>'
    if marker in html:
        html = html.replace(marker, marker + '<span class="integration-chip">6X CONNECT</span>', 1)
    html = html.replace("</body>", CAMERA_MODAL + "\n" + INTEGRATION_SCRIPT + "\n</body>")
    return html


open_core_layer.commercial_layer.reliable_layer.stable_layer.web_v8.CONTROL_CENTER_HTML = _enhance(
    open_core_layer.commercial_layer.reliable_layer.stable_layer.web_v8.CONTROL_CENTER_HTML
)
CONTROL_CENTER_HTML = open_core_layer.commercial_layer.reliable_layer.stable_layer.web_v8.CONTROL_CENTER_HTML


def main() -> None:
    import uvicorn

    uvicorn.run("hakham.web_v16:app", host="127.0.0.1", port=8765, reload=False)


if __name__ == "__main__":
    main()
