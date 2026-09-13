from __future__ import annotations

from fastapi import HTTPException
from pydantic import BaseModel, Field

from . import web_v9 as vision_web
from . import web_v19_7 as previous


app = previous.app


class LiveVisionRequest(BaseModel):
    data_url: str = Field(min_length=20)
    filename: str = Field(default="field-camera.jpg", max_length=240)
    context: str = Field(default="", max_length=2400)
    remember: bool = False


@app.post("/api/vision/live/analyze")
def analyze_live_vision(request: LiveVisionRequest) -> dict[str, object]:
    """Analyze one manually captured camera frame.

    Phase 1 is intentionally manual and economical: the browser preview is live,
    but no frame is sent until the Ach presses ANALISAR QUADRO. By default the
    frame is not persisted. Memory is only written when remember=True.
    """
    service = vision_web.vision
    if not service.configured:
        raise HTTPException(status_code=503, detail="Nenhum provedor de visão está configurado")

    image_bytes, mime_type = vision_web._decode_data_url(request.data_url)
    try:
        if request.remember:
            item = service.analyze_and_remember(
                image_bytes,
                mime_type,
                filename=request.filename,
                context=request.context,
            )
            description = item.description
            item_payload: dict[str, object] | None = item.as_dict()
        else:
            description = service.client.analyze(
                image_bytes,
                mime_type,
                context=request.context,
            )
            item_payload = None
    except vision_web.http_error_types() as exc:
        raise HTTPException(status_code=502, detail=f"Falha no provedor visual: {exc}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Falha na visão de campo: {exc}") from exc

    return {
        "ok": True,
        "answer": description,
        "saved": bool(request.remember),
        "item": item_payload,
        "provider": getattr(service, "active_provider", getattr(service, "provider", "vision")),
        "model": getattr(service.client, "model", "unknown"),
    }


FIELD_VISION_UI = r"""
<style id="hakham-v19-8-field-vision">
/* Phase 1: one live preview, one manual frame at a time. No background sampling. */
body.contextual-ready #chatPanel .compose{grid-template-columns:minmax(0,1fr) 52px 52px 52px 118px!important}
body.contextual-ready #chatPanel #contextImageBtn{grid-column:2!important;grid-row:1!important}
body.contextual-ready #chatPanel #fieldCameraBtn{grid-column:3!important;grid-row:1!important}
body.contextual-ready #chatPanel #chatMic{grid-column:4!important;grid-row:1!important}
body.contextual-ready #chatPanel #sendBtn{grid-column:5!important;grid-row:1!important}
.field-camera-btn{min-width:52px!important;min-height:52px!important;border:1px solid rgba(39,224,173,.38)!important;border-radius:12px!important;background:rgba(5,46,44,.82)!important;color:#d6fff5!important;font-size:18px!important;cursor:pointer!important;box-shadow:inset 0 0 20px rgba(39,224,173,.045)!important}
.field-camera-btn:hover{border-color:#62f4d1!important;box-shadow:0 0 20px rgba(39,224,173,.13),inset 0 0 20px rgba(39,224,173,.06)!important}
.field-camera-modal{position:fixed;inset:0;z-index:260;display:none;align-items:center;justify-content:center;padding:16px;background:rgba(0,3,9,.84);backdrop-filter:blur(13px)}
.field-camera-modal.open{display:flex}.field-camera-shell{width:min(930px,97vw);max-height:94vh;overflow:auto;border:1px solid rgba(39,224,173,.38);border-radius:20px;background:linear-gradient(145deg,rgba(4,20,33,.985),rgba(1,8,16,.985));box-shadow:0 30px 100px rgba(0,0,0,.68),0 0 70px rgba(39,224,173,.07) inset;padding:15px}
.field-camera-head{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:10px}.field-camera-title b{display:block;letter-spacing:.09em}.field-camera-title small{display:block;color:#78a49c;font-size:10px;margin-top:2px}.field-camera-live{display:inline-flex;align-items:center;gap:6px;margin-left:7px;color:#72ffd9;font-size:10px;font-weight:900;letter-spacing:.08em}.field-camera-live:before{content:"";width:7px;height:7px;border-radius:50%;background:#27e0ad;box-shadow:0 0 13px #27e0ad;animation:fieldBlink .8s ease-in-out infinite alternate}@keyframes fieldBlink{to{opacity:.34}}
.field-camera-close{border:1px solid rgba(255,100,123,.36);border-radius:9px;background:rgba(68,16,26,.65);color:#ffb4c0;padding:8px 11px;cursor:pointer}.field-camera-stage{position:relative;aspect-ratio:16/9;border:1px solid rgba(39,224,173,.22);border-radius:14px;overflow:hidden;background:#000}.field-camera-stage video{width:100%;height:100%;display:block;object-fit:cover}.field-camera-stage[data-facing="user"] video{transform:scaleX(-1)}.field-camera-stage:after{content:"";position:absolute;left:0;right:0;height:1px;top:8%;pointer-events:none;background:linear-gradient(90deg,transparent,#27e0ad,transparent);box-shadow:0 0 14px #27e0ad;animation:fieldScan 3.8s linear infinite}@keyframes fieldScan{0%{top:8%}50%{top:92%}100%{top:8%}}
.field-camera-controls{display:grid;grid-template-columns:1fr 1fr 1fr;gap:9px;margin-top:10px}.field-camera-controls button{min-height:44px;border:1px solid rgba(39,224,173,.34);border-radius:10px;background:rgba(7,48,49,.72);color:#e7fff8;font-weight:850;cursor:pointer}.field-camera-controls button.secondary{border-color:rgba(37,220,255,.28);background:rgba(5,35,55,.72);color:#d9f8ff}.field-camera-controls button.danger{border-color:rgba(255,100,123,.36);background:rgba(73,18,28,.66);color:#ffc0ca}.field-camera-controls button:disabled{opacity:.45;cursor:wait}
.field-camera-options{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-top:10px;padding:9px 10px;border:1px solid rgba(39,224,173,.16);border-radius:10px;background:rgba(2,20,27,.54);color:#8caaa9;font-size:11px}.field-camera-memory{display:flex;align-items:center;gap:7px;color:#c9efe5}.field-camera-memory input{accent-color:#27e0ad}.field-camera-result{margin-top:10px;min-height:54px;padding:10px 11px;border:1px solid rgba(37,220,255,.16);border-radius:10px;background:rgba(3,17,29,.62);color:#cae8f2;font-size:12px;white-space:pre-wrap}.field-camera-status{color:#72ffd9;font-weight:850;letter-spacing:.05em}.field-camera-note{margin-top:9px;color:#7896a4;font-size:10px;line-height:1.5}.field-camera-note b{color:#ff9aac}
@media(max-width:900px){
 body.contextual-ready #chatPanel .compose{grid-template-columns:minmax(0,1fr) 48px 48px 48px!important}
 body.contextual-ready #chatPanel .compose textarea{grid-column:1/-1!important;grid-row:1!important}
 body.contextual-ready #chatPanel #sendBtn{grid-column:1!important;grid-row:2!important}
 body.contextual-ready #chatPanel #contextImageBtn{grid-column:2!important;grid-row:2!important;min-width:48px!important;min-height:46px!important}
 body.contextual-ready #chatPanel #fieldCameraBtn{grid-column:3!important;grid-row:2!important;min-width:48px!important;min-height:46px!important}
 body.contextual-ready #chatPanel #chatMic{grid-column:4!important;grid-row:2!important;min-width:48px!important;min-height:46px!important}
 .field-camera-modal{padding:7px}.field-camera-shell{padding:10px;border-radius:15px;width:100%}.field-camera-controls{grid-template-columns:1fr 1fr}.field-camera-controls .danger{grid-column:1/-1}.field-camera-options{align-items:flex-start;flex-direction:column}
}
</style>
"""

FIELD_VISION_MODAL = r"""
<div class="field-camera-modal" id="fieldCameraModal" aria-hidden="true">
  <section class="field-camera-shell" role="dialog" aria-modal="true" aria-label="Visão de campo Hakham Infinity">
    <div class="field-camera-head">
      <div class="field-camera-title"><b>HAKHAM VISION // CAMPO <span class="field-camera-live">PREVIEW AO VIVO</span></b><small>FASE 1 · WEBCAM + CÂMERA DO CELULAR · CAPTURA MANUAL</small></div>
      <button class="field-camera-close" id="fieldCameraClose" type="button">ENCERRAR</button>
    </div>
    <div class="field-camera-stage" id="fieldCameraStage" data-facing="environment"><video id="fieldCameraVideo" autoplay playsinline muted></video></div>
    <div class="field-camera-controls">
      <button id="fieldCameraCapture" type="button">📷 ANALISAR QUADRO</button>
      <button class="secondary" id="fieldCameraSwitch" type="button">↻ TROCAR CÂMERA</button>
      <button class="danger" id="fieldCameraStop" type="button">■ DESLIGAR</button>
    </div>
    <div class="field-camera-options">
      <label class="field-camera-memory"><input id="fieldCameraRemember" type="checkbox"> SALVAR ESTE QUADRO NA MEMÓRIA VISUAL</label>
      <span>Sem marcação, a análise é temporária e a imagem não é persistida.</span>
    </div>
    <div class="field-camera-result" id="fieldCameraResult"><span class="field-camera-status">PRONTO</span> · Mostre o ambiente e toque em ANALISAR QUADRO quando quiser minha leitura.</div>
    <div class="field-camera-note"><b>Privacidade:</b> áudio sempre desligado. Nenhum vídeo é enviado continuamente. No celular, abra o Hakham pelo endereço HTTPS para liberar a câmera traseira.</div>
  </section>
</div>
"""

FIELD_VISION_SCRIPT = r"""
<script id="hakham-v19-8-field-vision-js">
(function(){
  const compose=document.querySelector('#chatPanel .compose');
  const input=document.querySelector('#chatInput');
  const mic=document.querySelector('#chatMic');
  if(!compose||!input)return;

  let cameraBtn=document.querySelector('#fieldCameraBtn');
  if(!cameraBtn){cameraBtn=document.createElement('button');cameraBtn.id='fieldCameraBtn';cameraBtn.type='button';cameraBtn.className='field-camera-btn';cameraBtn.title='Visão de campo';cameraBtn.setAttribute('aria-label','Abrir visão de campo');cameraBtn.textContent='◉';if(mic)mic.insertAdjacentElement('beforebegin',cameraBtn);else compose.appendChild(cameraBtn)}

  const modal=document.querySelector('#fieldCameraModal');
  const video=document.querySelector('#fieldCameraVideo');
  const stage=document.querySelector('#fieldCameraStage');
  const captureBtn=document.querySelector('#fieldCameraCapture');
  const switchBtn=document.querySelector('#fieldCameraSwitch');
  const stopBtn=document.querySelector('#fieldCameraStop');
  const closeBtn=document.querySelector('#fieldCameraClose');
  const remember=document.querySelector('#fieldCameraRemember');
  const result=document.querySelector('#fieldCameraResult');
  let stream=null;
  let facing=(window.matchMedia&&window.matchMedia('(pointer:coarse)').matches)||window.innerWidth<=900?'environment':'user';

  function bubble(role,text){try{if(typeof addBubble==='function')addBubble(role,text)}catch(e){}}
  function toastSafe(text){try{if(typeof toast==='function')toast(text)}catch(e){}}
  function state(name,label){try{if(typeof setState==='function')setState(name,label)}catch(e){}}
  function status(text){if(result)result.textContent=text}
  function stopTracks(){if(stream){stream.getTracks().forEach(function(track){try{track.stop()}catch(e){}});stream=null}if(video)video.srcObject=null}

  async function acquire(preferred){
    stopTracks();facing=preferred;
    if(!navigator.mediaDevices||!navigator.mediaDevices.getUserMedia)throw new Error('Este navegador não oferece acesso à câmera');
    const constraints={video:{facingMode:{ideal:preferred},width:{ideal:1280},height:{ideal:720}},audio:false};
    try{stream=await navigator.mediaDevices.getUserMedia(constraints)}catch(first){stream=await navigator.mediaDevices.getUserMedia({video:true,audio:false})}
    if(video){video.srcObject=stream;await video.play().catch(function(){})}
    try{const track=stream.getVideoTracks()[0],settings=track&&track.getSettings?track.getSettings():{};if(settings&&settings.facingMode)facing=settings.facingMode}catch(e){}
    if(stage)stage.dataset.facing=facing==='user'?'user':'environment';
  }

  async function openCamera(){
    if(!window.isSecureContext&&!/^(localhost|127\.0\.0\.1)$/.test(location.hostname)){bubble('HAKHAM · VISÃO','A câmera do navegador exige HTTPS. Abra o domínio protegido do Hakham no celular.');return}
    try{state('executing','ABRINDO CÂMERA');await acquire(facing);modal?.classList.add('open');modal?.setAttribute('aria-hidden','false');document.body.classList.add('field-vision-live');status('PRONTO · Preview ao vivo. Nenhum quadro foi enviado.');toastSafe(facing==='environment'?'Câmera traseira ativa':'Webcam ativa')}catch(e){stopTracks();state('idle','PRONTO');bubble('HAKHAM · VISÃO','Não consegui abrir a câmera: '+(e.message||e)+'. Confira a permissão do navegador.');status('ERRO · '+(e.message||e))}
  }

  function closeCamera(){stopTracks();modal?.classList.remove('open');modal?.setAttribute('aria-hidden','true');document.body.classList.remove('field-vision-live');state('idle','PRONTO')}

  async function switchCamera(){
    const next=facing==='user'?'environment':'user';
    switchBtn.disabled=true;status('TROCANDO CÂMERA...');
    try{await acquire(next);status((facing==='environment'?'CÂMERA TRASEIRA':'CÂMERA FRONTAL')+' · Preview ao vivo.')}catch(e){status('Não consegui trocar a câmera: '+(e.message||e))}finally{switchBtn.disabled=false}
  }

  async function captureFrame(){
    if(!stream||!video||!video.videoWidth){toastSafe('A câmera ainda não está pronta');return}
    const maxWidth=1280;const width=Math.min(video.videoWidth,maxWidth);const height=Math.max(1,Math.round(width*(video.videoHeight/video.videoWidth)));const canvas=document.createElement('canvas');canvas.width=width;canvas.height=height;const ctx=canvas.getContext('2d');if(!ctx)return;
    if(facing==='user'){ctx.translate(width,0);ctx.scale(-1,1)}ctx.drawImage(video,0,0,width,height);
    const dataUrl=canvas.toDataURL('image/jpeg',.82);const filename='campo-'+new Date().toISOString().replace(/[:.]/g,'-')+'.jpg';
    const typed=input.value.trim();const context=typed||'Visita técnica em campo. Analise o que está visível e destaque oportunidades de comunicação visual, fachada, sinalização, ambientação, leitura, fluxo, pontos de instalação, riscos técnicos e perguntas que devemos fazer ao cliente. Diferencie observação de hipótese.';
    const save=!!remember?.checked;
    captureBtn.disabled=true;switchBtn.disabled=true;state('thinking','ANALISANDO CAMPO');status('ANALISANDO QUADRO · '+(save?'com memória':'temporário')+'...');
    try{
      const r=await fetch('/api/vision/live/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({data_url:dataUrl,filename:filename,context:context,remember:save})});let d={};try{d=await r.json()}catch(e){}if(!r.ok)throw new Error(d.detail||('HTTP '+r.status));
      const provider=String(d.provider||'visão').toUpperCase();const model=String(d.model||'');const answer=String(d.answer||'Quadro analisado.');status((save?'MEMORIZADO':'ANÁLISE TEMPORÁRIA')+' · '+provider+(model?' · '+model:'')+'\n\n'+answer);bubble('HAKHAM · VISÃO DE CAMPO',answer);try{if(typeof speakHakham==='function')speakHakham(answer)}catch(e){};toastSafe(save?'Quadro analisado e salvo na memória':'Quadro analisado sem salvar na memória')
    }catch(e){status('ATENÇÃO · '+(e.message||e));bubble('HAKHAM · VISÃO DE CAMPO','Falha ao analisar o quadro: '+(e.message||e))}
    finally{captureBtn.disabled=false;switchBtn.disabled=false;state('idle','PRONTO')}
  }

  function openIntent(text){return /(?:ative|ativar|ligue|abr[ae]|inicie|mostre).{0,24}(?:webcam|c[aâ]mera|vis[aã]o ao vivo|vis[aã]o de campo)/i.test(text||'')||/(?:webcam|c[aâ]mera do celular|vis[aã]o de campo).{0,18}(?:ative|abr[ae]|ligue|inicie)/i.test(text||'')}
  function closeIntent(text){return /(?:desative|desligue|feche|pare|encerre).{0,24}(?:webcam|c[aâ]mera|vis[aã]o ao vivo|vis[aã]o de campo)/i.test(text||'')}
  function interceptText(){const text=input.value.trim();if(!text)return false;if(closeIntent(text)){input.value='';bubble('ACH',text);closeCamera();bubble('HAKHAM','Visão de campo encerrada.');return true}if(openIntent(text)){input.value='';bubble('ACH',text);openCamera();return true}return false}

  document.addEventListener('click',function(event){
    const fieldButton=event.target.closest&&event.target.closest('#fieldCameraBtn');
    const oldWebcam=event.target.closest&&event.target.closest('#webcamBtn');
    const tool=event.target.closest&&event.target.closest('#toolGrid .tool[data-tool="webcam.capture"]');
    const send=event.target.closest&&event.target.closest('#sendBtn');
    if(fieldButton||oldWebcam||tool){event.preventDefault();event.stopImmediatePropagation();openCamera();return}
    if(send&&interceptText()){event.preventDefault();event.stopImmediatePropagation()}
  },true);
  document.addEventListener('keydown',function(event){if(event.target===input&&event.key==='Enter'&&!event.shiftKey&&interceptText()){event.preventDefault();event.stopImmediatePropagation()}},true);

  captureBtn?.addEventListener('click',captureFrame);switchBtn?.addEventListener('click',switchCamera);stopBtn?.addEventListener('click',closeCamera);closeBtn?.addEventListener('click',closeCamera);modal?.addEventListener('click',function(event){if(event.target===modal)closeCamera()});
  document.addEventListener('visibilitychange',function(){if(document.hidden&&stream)closeCamera()});window.addEventListener('beforeunload',closeCamera);
})();
</script>
"""


def _enhance(html: str) -> str:
    html = html.replace("Orbit Command v0.19.7 Vision Router", "Orbit Command v0.19.8 Field Vision Phase 1")
    html = html.replace("ORBIT COMMAND // v0.19.7 VISION ROUTER", "ORBIT COMMAND // v0.19.8 FIELD VISION PHASE 1")
    html = html.replace("HAKHAM INFINITY ∞ v0.19.7 // SER Comtec", "HAKHAM INFINITY ∞ v0.19.8 // SER Comtec")
    html = html.replace("</head>", FIELD_VISION_UI + "\n</head>")
    html = html.replace("</body>", FIELD_VISION_MODAL + "\n" + FIELD_VISION_SCRIPT + "\n</body>")
    return html


_stable_web = previous._stable_web
_stable_web.CONTROL_CENTER_HTML = _enhance(_stable_web.CONTROL_CENTER_HTML)
CONTROL_CENTER_HTML = _stable_web.CONTROL_CENTER_HTML


def main() -> None:
    import uvicorn

    uvicorn.run("hakham.web_v19_8:app", host="127.0.0.1", port=8765, reload=False)


if __name__ == "__main__":
    main()
