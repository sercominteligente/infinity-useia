from __future__ import annotations

import base64
import binascii

from fastapi import HTTPException, Query
from pydantic import BaseModel, Field

from . import web as backend
from . import web_v8 as previous
from .vision import ALLOWED_IMAGE_TYPES, MAX_IMAGE_BYTES, VisionService


app = previous.app
vision = VisionService()


class VisionRequest(BaseModel):
    data_url: str = Field(min_length=20)
    filename: str = Field(default="image", max_length=240)
    context: str = Field(default="", max_length=2000)


def _decode_data_url(data_url: str) -> tuple[bytes, str]:
    try:
        header, encoded = data_url.split(",", 1)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid image data URL") from exc
    if not header.startswith("data:") or ";base64" not in header:
        raise HTTPException(status_code=400, detail="image must be a base64 data URL")
    mime_type = header[5:].split(";", 1)[0].strip().lower()
    if mime_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=415, detail=f"unsupported image type: {mime_type}")
    try:
        image_bytes = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise HTTPException(status_code=400, detail="invalid base64 image") from exc
    if not image_bytes:
        raise HTTPException(status_code=400, detail="empty image")
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="image exceeds 12 MB limit")
    return image_bytes, mime_type


@app.post("/api/vision/analyze")
def analyze_visual_memory(request: VisionRequest) -> dict[str, object]:
    if not vision.configured:
        raise HTTPException(status_code=503, detail="Visual sensor not configured: OPENAI_API_KEY is missing")
    image_bytes, mime_type = _decode_data_url(request.data_url)
    try:
        item = vision.analyze_and_remember(
            image_bytes,
            mime_type,
            filename=request.filename,
            context=request.context,
        )
        answer = backend.runtime.core().observe_visual(
            filename=request.filename,
            description=item.description,
            user_context=request.context,
        )
    except http_error_types() as exc:
        raise HTTPException(status_code=502, detail=f"visual analysis failed: {exc}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Hakham visual grounding failed: {exc}") from exc
    return {"ok": True, "item": item.as_dict(), "answer": answer}


def http_error_types() -> tuple[type[Exception], ...]:
    import httpx

    return (httpx.HTTPError,)


@app.get("/api/vision/recent")
def recent_visual_memory(limit: int = Query(default=8, ge=1, le=50)) -> dict[str, object]:
    items = [item.as_dict() for item in vision.store.recent(limit)]
    return {"items": items, "count": len(items), "configured": vision.configured, "model": vision.client.model}


VISION_UI = r"""
<style id="hakham-v09-vision">
.visionbar{display:flex;align-items:center;gap:9px;margin:0 0 9px;padding:8px 10px;border:1px solid rgba(37,220,255,.22);border-radius:11px;background:rgba(4,23,38,.52)}
.visionbar button{border:1px solid rgba(37,220,255,.42);border-radius:9px;background:rgba(7,45,67,.78);color:#dffaff;padding:8px 12px;font-weight:750;cursor:pointer}.visionbar button:hover{border-color:#62efff}.visionbar small{color:#87aab9}.visionbar .vready{margin-left:auto;color:#27e0ad;font-size:12px}.vision-preview{max-width:220px;max-height:150px;display:block;border-radius:9px;margin-top:7px;border:1px solid rgba(75,210,255,.28);object-fit:contain}
@media(max-width:640px){.visionbar{flex-wrap:wrap}.visionbar .vready{margin-left:0;width:100%}.visionbar button{width:100%}.vision-preview{max-width:180px}}
</style>
"""

VISION_BAR = r"""<div class="visionbar"><input id="visionFile" type="file" accept="image/png,image/jpeg,image/webp,image/gif" hidden><button id="visionBtn" type="button">👁 VISÃO + MEMÓRIA</button><small>Envie uma imagem. O Hakham vê, responde e guarda a memória visual em segundo plano.</small><span class="vready" id="visionState">SENSOR PRONTO</span></div>"""

VISION_SCRIPT = r"""
<script id="hakham-v09-vision-js">
(function(){
  const fileInput=document.querySelector('#visionFile'),visionBtn=document.querySelector('#visionBtn'),visionState=document.querySelector('#visionState');
  if(!fileInput||!visionBtn)return;
  function visualBubble(who,text,cls,imgUrl){
    const log=document.querySelector('#chatLog'); if(!log)return;
    const b=document.createElement('div'); b.className='bubble'+(cls?' '+cls:'');
    const s=document.createElement('strong'); s.textContent=who; b.appendChild(s);
    const t=document.createElement('div'); t.textContent=text; b.appendChild(t);
    if(imgUrl){const im=document.createElement('img');im.src=imgUrl;im.className='vision-preview';im.alt='Imagem enviada ao Hakham';b.appendChild(im)}
    log.appendChild(b); log.scrollTop=log.scrollHeight;
  }
  function toDataURL(file){return new Promise((resolve,reject)=>{const r=new FileReader();r.onload=()=>resolve(String(r.result));r.onerror=()=>reject(r.error||new Error('Falha ao ler imagem'));r.readAsDataURL(file)})}
  visionBtn.addEventListener('click',()=>fileInput.click());
  fileInput.addEventListener('change',async()=>{
    const file=fileInput.files&&fileInput.files[0]; if(!file)return;
    if(file.size>12*1024*1024){if(typeof toast==='function')toast('Imagem maior que 12 MB');fileInput.value='';return}
    const preview=URL.createObjectURL(file); visualBubble('ACH · IMAGEM',file.name,'user',preview);
    visionState.textContent='ANALISANDO'; if(typeof setState==='function')setState('thinking','VISÃO ATIVA');
    try{
      const dataUrl=await toDataURL(file);
      const context=(document.querySelector('#chatInput')?.value||'').trim();
      const r=await fetch('/api/vision/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({data_url:dataUrl,filename:file.name,context})});
      let d={}; try{d=await r.json()}catch(e){}
      if(!r.ok)throw new Error(d.detail||('HTTP '+r.status));
      const item=d.item||{};
      visualBubble('HAKHAM · VISÃO',d.answer||item.description||'Imagem analisada e memorizada.','');
      visionState.textContent='VISÃO MEMORIZADA'; if(typeof toast==='function')toast('Hakham viu a imagem e guardou a memória');
      if(typeof speakHakham==='function'&&d.answer)speakHakham(d.answer);
    }catch(e){visualBubble('HAKHAM · VISÃO','Não consegui concluir a análise: '+e.message,'');visionState.textContent='ERRO';if(typeof toast==='function')toast('Visão: '+e.message)}
    finally{if(typeof setState==='function')setState('idle','EM ESPERA');fileInput.value='';setTimeout(()=>{if(visionState.textContent!=='ERRO')visionState.textContent='SENSOR PRONTO'},2600)}
  });
})();
</script>
"""


def _enhance_html(html: str) -> str:
    html = html.replace("Orbit Command v0.7.1", "Orbit Command v0.9 Vision")
    html = html.replace("ORBIT COMMAND // v0.7.1", "ORBIT COMMAND // v0.9 VISION")
    html = html.replace("HAKHAM INFINITY ∞ v0.7.1 // SER Comtec", "HAKHAM INFINITY ∞ v0.9 // SER Comtec")
    html = html.replace("</head>", VISION_UI + "\n</head>")
    html = html.replace('<div class="compose">', VISION_BAR + '<div class="compose">', 1)
    html = html.replace("</body>", VISION_SCRIPT + "\n</body>")
    return html


previous.CONTROL_CENTER_HTML = _enhance_html(previous.CONTROL_CENTER_HTML)


def main() -> None:
    import uvicorn

    uvicorn.run("hakham.web_v9:app", host="127.0.0.1", port=8765, reload=False)


if __name__ == "__main__":
    main()
