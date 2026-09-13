from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel, Field

from . import web_v3 as previous
from .config import load_settings
from .voice import OpenAITTSClient


app = FastAPI(title="HAKHAM Infinity Control Center", version="0.4.1")


class SpeechRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4096)


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return CONTROL_CENTER_HTML


@app.get("/api/status")
def status() -> dict[str, object]:
    payload = previous.status()
    settings = load_settings()
    payload.update(
        {
            "version": "0.4.1",
            "openai_tts_ready": bool(settings.openai_api_key),
            "openai_tts_model": settings.openai_tts_model,
            "openai_tts_voice": settings.openai_tts_voice,
            "voice_latency_mode": "fast",
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
def search_memory(
    q: str = Query(default="", max_length=500),
    limit: int = Query(default=8, ge=1, le=50),
) -> dict[str, object]:
    return previous.search_memory(q=q, limit=limit)


@app.post("/api/memory")
def create_memory(request: previous.backend.ManualMemoryRequest) -> dict[str, object]:
    return previous.create_memory(request)


@app.get("/api/models")
def models() -> dict[str, object]:
    return previous.models()


@app.post("/api/mode")
def set_mode(request: previous.backend.ModeRequest) -> dict[str, object]:
    return previous.set_mode(request)


@app.post("/api/chat")
def chat(request: previous.backend.ChatRequest) -> dict[str, str]:
    return previous.chat(request)


@app.post("/api/voice/speech")
def speech(request: SpeechRequest) -> Response:
    settings = load_settings()
    if not settings.openai_api_key:
        raise HTTPException(status_code=503, detail="OpenAI natural voice is not configured")

    client = OpenAITTSClient(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        model=settings.openai_tts_model,
        voice=settings.openai_tts_voice,
        speed=settings.openai_tts_speed,
        instructions=settings.openai_tts_instructions,
    )
    try:
        audio = client.synthesize(request.text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Natural voice unavailable: {exc}") from exc

    return Response(
        content=audio,
        media_type="audio/mpeg",
        headers={"Cache-Control": "no-store"},
    )


def main() -> None:
    import uvicorn

    uvicorn.run("hakham.web_v4:app", host="127.0.0.1", port=8765, reload=False)


VOICE_UI = r'''
<script>
let hakhamNaturalAudio=null;
let hakhamNaturalReady=false;
let hakhamVoiceEngine=localStorage.getItem('hakhamVoiceEngine')||'openai';
let hakhamSpeechGeneration=0;
const hakhamBrowserSpeak=speak;
const hakhamBrowserStop=stopSpeech;

function splitHakhamSpeech(text){
  const clean=String(text||'').replace(/\s+/g,' ').trim();
  if(!clean)return [];
  const sentences=clean.match(/[^.!?;:]+[.!?;:]+|[^.!?;:]+$/g)||[clean];
  const chunks=[];
  let current='';
  const pushCurrent=()=>{const c=current.trim();if(c)chunks.push(c);current=''};
  for(const raw of sentences){
    const sentence=raw.trim();
    if(!sentence)continue;
    const limit=chunks.length===0?190:360;
    if(!current&&sentence.length>limit){
      const parts=sentence.match(/.{1,170}(?:,|\s|$)|.{1,170}/g)||[sentence];
      for(const part of parts){const p=part.trim();if(p)chunks.push(p)}
      continue;
    }
    const candidate=(current+' '+sentence).trim();
    if(candidate.length<=limit){current=candidate}else{pushCurrent();current=sentence}
  }
  pushCurrent();
  return chunks;
}

function refreshVoiceEngineButton(){
  const b=document.querySelector('#voiceEngine');if(!b)return;
  const natural=hakhamVoiceEngine==='openai'&&hakhamNaturalReady;
  b.classList.toggle('active',natural);
  b.textContent=natural?'✨ GPT VOICE FAST':'🔊 VOZ NAVEGADOR';
  b.title=hakhamNaturalReady?'Alternar entre GPT Natural e voz do navegador':'Configure OPENAI_API_KEY para habilitar GPT Natural';
}

async function fetchHakhamNaturalChunk(text,generation){
  const started=performance.now();
  const r=await fetch('/api/voice/speech',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text})});
  if(generation!==hakhamSpeechGeneration)throw new Error('speech-cancelled');
  if(!r.ok){let detail='falha na voz natural';try{detail=(await r.json()).detail||detail}catch(e){}throw new Error(detail)}
  const blob=await r.blob();
  if(generation!==hakhamSpeechGeneration)throw new Error('speech-cancelled');
  return {url:URL.createObjectURL(blob),latencyMs:Math.round(performance.now()-started)};
}

async function playHakhamAudio(item,generation){
  if(generation!==hakhamSpeechGeneration){URL.revokeObjectURL(item.url);throw new Error('speech-cancelled')}
  const audio=new Audio(item.url);audio.preload='auto';hakhamNaturalAudio=audio;
  await new Promise((resolve,reject)=>{audio.onended=resolve;audio.onerror=()=>reject(new Error('falha ao reproduzir áudio'));audio.play().catch(reject)});
  URL.revokeObjectURL(item.url);hakhamNaturalAudio=null;
}

async function speakNatural(text){
  hakhamBrowserStop();
  const chunks=splitHakhamSpeech(text);
  if(!chunks.length)return;
  const generation=++hakhamSpeechGeneration;
  isSpeaking=true;setHakhamState('speaking','HAKHAM FALANDO · GPT FAST');
  try{
    let pending=fetchHakhamNaturalChunk(chunks[0],generation);
    for(let i=0;i<chunks.length;i++){
      const current=await pending;
      if(i===0){const vs=document.querySelector('#voiceStatus');if(vs)vs.textContent=`GPT Voice pronta em ${(current.latencyMs/1000).toFixed(1)}s`}
      const next=i+1<chunks.length?fetchHakhamNaturalChunk(chunks[i+1],generation):null;
      await playHakhamAudio(current,generation);
      pending=next;
    }
  }catch(e){
    if(e.message==='speech-cancelled')return;
    toast('GPT Voice indisponível. Usando voz do navegador.');
    isSpeaking=false;hakhamBrowserSpeak(text);return;
  }
  if(generation===hakhamSpeechGeneration){isSpeaking=false;setHakhamState('idle','EM ESPERA')}
}

speak=function(text){
  if(!voiceEnabled||!text)return;
  if(hakhamVoiceEngine==='openai'&&hakhamNaturalReady){speakNatural(text);return}
  hakhamBrowserSpeak(text);
};

stopSpeech=function(){
  hakhamSpeechGeneration++;
  if(hakhamNaturalAudio){try{hakhamNaturalAudio.pause();hakhamNaturalAudio.currentTime=0}catch(e){}hakhamNaturalAudio=null}
  hakhamBrowserStop();
};

document.querySelector('#stopVoice').onclick=stopSpeech;
const voiceActions=document.querySelector('.voice-actions');
if(voiceActions){
  const engine=document.createElement('button');engine.className='voicebtn';engine.id='voiceEngine';engine.type='button';
  engine.onclick=()=>{if(!hakhamNaturalReady){toast('Adicione OPENAI_API_KEY no .env para ativar GPT Natural.');return}hakhamVoiceEngine=hakhamVoiceEngine==='openai'?'browser':'openai';localStorage.setItem('hakhamVoiceEngine',hakhamVoiceEngine);refreshVoiceEngineButton();toast(hakhamVoiceEngine==='openai'?'GPT Voice Fast ativada':'Voz do navegador ativada')};
  voiceActions.appendChild(engine);
}

(async()=>{
  try{
    const r=await fetch('/api/status');const s=await r.json();hakhamNaturalReady=!!s.openai_tts_ready;
    if(!hakhamNaturalReady&&hakhamVoiceEngine==='openai')hakhamVoiceEngine='browser';
    refreshVoiceEngineButton();
    const support=document.querySelector('#voiceSupport');
    if(support)support.textContent=hakhamNaturalReady?`GPT Voice FAST · ${s.openai_tts_model} · ${s.openai_tts_voice}`:'GPT Voice não configurada · navegador como fallback';
  }catch(e){hakhamNaturalReady=false;hakhamVoiceEngine='browser';refreshVoiceEngineButton()}
})();
</script>
'''

CONTROL_CENTER_HTML = (
    previous.CONTROL_CENTER_HTML
    .replace("HAKHAM INFINITY ∞ v0.3", "HAKHAM INFINITY ∞ v0.4.1")
    .replace("</body>", VOICE_UI + "\n</body>")
)
