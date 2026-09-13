from __future__ import annotations

import os
import time
from typing import Any

import httpx
from dotenv import load_dotenv
from fastapi import HTTPException
from pydantic import BaseModel, Field

from . import web_v12 as stable_layer


app = stable_layer.app


class ReliableWhatsAppRequest(BaseModel):
    number: str = Field(min_length=8, max_length=32)
    text: str = Field(min_length=1, max_length=20_000)
    approved: bool = False


def _evolution_settings() -> tuple[str, str, str]:
    load_dotenv()
    return (
        os.getenv("EVOLUTION_API_URL", "").strip().rstrip("/"),
        os.getenv("EVOLUTION_API_KEY", "").strip(),
        os.getenv("EVOLUTION_INSTANCE", "").strip(),
    )


def _safe_upstream_detail(response: httpx.Response) -> str:
    try:
        payload = response.json()
        if isinstance(payload, dict):
            nested = payload.get("response")
            if isinstance(nested, dict) and nested.get("message"):
                return str(nested.get("message"))[:1200]
            for key in ("message", "error", "detail"):
                if payload.get(key):
                    return str(payload.get(key))[:1200]
    except Exception:
        pass
    text = (response.text or "").strip()
    return text[:1200] if text else f"HTTP {response.status_code} sem detalhe"


def _connection_state(base_url: str, api_key: str, instance: str) -> str:
    try:
        with httpx.Client(timeout=12.0) as client:
            response = client.get(
                f"{base_url}/instance/connectionState/{instance}",
                headers={"apikey": api_key},
            )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            return ""
        root = payload.get("instance") if isinstance(payload.get("instance"), dict) else payload
        return str(root.get("state") or root.get("status") or "").strip().casefold()
    except Exception:
        return ""


@app.post("/api/whatsapp/send-reliable")
def send_whatsapp_reliable(request: ReliableWhatsAppRequest) -> dict[str, Any]:
    if not request.approved:
        raise HTTPException(status_code=403, detail="Aprovação explícita do Ach é obrigatória para envio pelo WhatsApp")

    base_url, api_key, instance = _evolution_settings()
    if not (base_url and api_key and instance):
        raise HTTPException(status_code=503, detail="Evolution não configurada no .env")

    number = "".join(ch for ch in request.number if ch.isdigit())
    text = request.text.strip()
    if not number or not text:
        raise HTTPException(status_code=400, detail="Número e mensagem são obrigatórios")

    endpoint = f"{base_url}/message/sendText/{instance}"
    timeout = httpx.Timeout(connect=12.0, read=60.0, write=30.0, pool=12.0)
    payload = {"number": number, "text": text}

    def attempt() -> httpx.Response:
        with httpx.Client(timeout=timeout) as client:
            return client.post(
                endpoint,
                headers={"apikey": api_key, "Content-Type": "application/json"},
                json=payload,
            )

    try:
        response = attempt()
    except httpx.ReadTimeout as exc:
        raise HTTPException(
            status_code=504,
            detail=(
                "A Evolution demorou mais de 60s para responder. O estado de entrega ficou incerto; "
                "confira o WhatsApp antes de reenviar para evitar mensagem duplicada."
            ),
        ) from exc
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Falha de comunicação com a Evolution: {type(exc).__name__}: {exc}") from exc

    if response.is_success:
        try:
            body = response.json()
        except Exception:
            body = {"raw": response.text[:1200]}
        return {"ok": True, "upstream_status": response.status_code, "result": body}

    detail = _safe_upstream_detail(response)
    lowered = detail.casefold()

    # Evolution/Baileys can report Connection Closed even while connectionState
    # still says open. A single retry is safe for this explicit pre-send failure.
    if response.status_code >= 500 and "connection closed" in lowered:
        state = _connection_state(base_url, api_key, instance)
        if state in {"open", "connected", "online", "ready"}:
            time.sleep(1.2)
            try:
                retry = attempt()
            except httpx.RequestError as exc:
                raise HTTPException(status_code=502, detail=f"Evolution perdeu a conexão durante a nova tentativa: {exc}") from exc
            if retry.is_success:
                try:
                    body = retry.json()
                except Exception:
                    body = {"raw": retry.text[:1200]}
                return {"ok": True, "upstream_status": retry.status_code, "retried": True, "result": body}
            detail = _safe_upstream_detail(retry)
            response = retry

    raise HTTPException(
        status_code=502,
        detail=f"Evolution respondeu HTTP {response.status_code}: {detail}",
    )


WHATSAPP_RELIABILITY_UI = r"""
<style id="hakham-v13-wa-reliability">
.wa-diagnostic{display:block;margin-top:5px;color:#789f9a;font-size:11px}.wa-diagnostic strong{color:#58efc4}
</style>
"""

WHATSAPP_RELIABILITY_SCRIPT = r"""
<script id="hakham-v13-wa-reliability-js">
(function(){
  const btn=document.querySelector('#waSendBtn');
  const number=document.querySelector('#waNumber');
  if(!btn||!number)return;
  const small=btn.closest('.wabar')?.querySelector('small');
  if(small){const note=document.createElement('span');note.className='wa-diagnostic';note.innerHTML='<strong>ENVIO REFORÇADO</strong> · timeout ampliado e diagnóstico do erro real da Evolution';small.appendChild(note)}

  function bubble(role,text){if(typeof addBubble==='function'){addBubble(role,text);return}const log=document.querySelector('#chatLog');if(!log)return;const d=document.createElement('div');d.className='bubble';const s=document.createElement('strong');s.textContent=role;d.appendChild(s);d.appendChild(document.createTextNode(text));log.appendChild(d);log.scrollTop=log.scrollHeight}
  function upstreamId(result){const root=result?.result||result||{};return root?.key?.id||root?.id||root?.messageId||''}

  btn.addEventListener('click',async function(event){
    event.preventDefault();
    event.stopImmediatePropagation();
    const phone=number.value.replace(/\D/g,'');
    const input=document.querySelector('#chatInput');
    const text=(input?.value||'').trim();
    if(!phone){if(typeof toast==='function')toast('Informe o número com DDI e DDD');number.focus();return}
    if(!text){if(typeof toast==='function')toast('Escreva a mensagem no campo do chat');input?.focus();return}

    try{
      const statusResponse=await fetch('/api/tools/execute',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({tool_id:'whatsapp.status',arguments:{},approved:false})});
      let statusData={};try{statusData=await statusResponse.json()}catch(e){}
      if(!statusResponse.ok)throw new Error(statusData.detail||('HTTP '+statusResponse.status));
    }catch(e){bubble('HAKHAM · WHATSAPP','Não vou enviar enquanto a conexão da Evolution não puder ser confirmada: '+e.message);return}

    const approved=window.confirm('Autorizar HAKHAM Infinity a enviar esta mensagem pelo WhatsApp para '+phone+'?\n\n'+text);
    if(!approved){if(typeof toast==='function')toast('Envio cancelado pelo Ach');return}

    btn.disabled=true;btn.textContent='ENVIANDO...';if(typeof setState==='function')setState('executing','WHATSAPP');
    try{
      const response=await fetch('/api/whatsapp/send-reliable',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({number:phone,text:text,approved:true})});
      let data={};try{data=await response.json()}catch(e){}
      if(!response.ok)throw new Error(data.detail||('HTTP '+response.status));
      const id=upstreamId(data.result);
      bubble('HAKHAM · WHATSAPP','Envio aceito pela Evolution para '+phone+(id?' · ID '+id:'')+(data.retried?' · conexão recuperada automaticamente':'')+'.');
      if(typeof toast==='function')toast('WhatsApp aceito pela Evolution');
      if(input)input.value='';
    }catch(e){bubble('HAKHAM · WHATSAPP','Falha no envio: '+e.message);if(typeof toast==='function')toast('WhatsApp: '+e.message)}
    finally{btn.disabled=false;btn.textContent='PREPARAR ENVIO';if(typeof setState==='function')setState('idle','EM ESPERA')}
  },true);
})();
</script>
"""


def _enhance(html: str) -> str:
    html = html.replace("Orbit Command v0.12 Stable Demo", "Orbit Command v0.13 Reliable WA")
    html = html.replace("ORBIT COMMAND // v0.12 STABLE DEMO", "ORBIT COMMAND // v0.13 RELIABLE WA")
    html = html.replace("HAKHAM INFINITY ∞ v0.12 // SER Comtec", "HAKHAM INFINITY ∞ v0.13 // SER Comtec")
    html = html.replace("</head>", WHATSAPP_RELIABILITY_UI + "\n</head>")
    html = html.replace("</body>", WHATSAPP_RELIABILITY_SCRIPT + "\n</body>")
    return html


stable_layer.web_v8.CONTROL_CENTER_HTML = _enhance(stable_layer.web_v8.CONTROL_CENTER_HTML)
CONTROL_CENTER_HTML = stable_layer.web_v8.CONTROL_CENTER_HTML


def main() -> None:
    import uvicorn

    uvicorn.run("hakham.web_v13:app", host="127.0.0.1", port=8765, reload=False)


if __name__ == "__main__":
    main()
