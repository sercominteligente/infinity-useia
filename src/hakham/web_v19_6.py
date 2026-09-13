from __future__ import annotations

from . import core as core_module
from . import web_research
from . import web_v9 as vision_web
from . import web_v19_5 as previous
from .gemini_bridge import GeminiWebResearchService, HybridVisionService


app = previous.app

# v0.19.6 changes backend providers without touching the contextual card logic.
vision_web.vision = HybridVisionService()
web_research.WebResearchService = GeminiWebResearchService
core_module.WebResearchService = GeminiWebResearchService


PRECISION_UI = r"""
<style id="hakham-v19-6-precision-pass">
/* Stronger deep-space layer. */
body.contextual-ready{background:#01040d!important}
body.contextual-ready .page,body.contextual-ready .stage{background:transparent!important}
body.contextual-ready .stage{position:relative!important;z-index:2!important}
body.contextual-ready #hakhamCore{isolation:auto!important;z-index:3!important;background:transparent!important}
.hakham-cosmos{
  display:block!important;position:fixed!important;inset:64px 0 0!important;z-index:1!important;
  opacity:1!important;overflow:hidden!important;pointer-events:none!important;
  background:
    radial-gradient(ellipse at 79% 21%,rgba(141,196,255,.34),rgba(57,105,211,.18) 12%,transparent 30%),
    radial-gradient(ellipse at 66% 36%,rgba(40,106,255,.20),transparent 36%),
    radial-gradient(ellipse at 22% 53%,rgba(0,195,255,.16),transparent 33%),
    radial-gradient(ellipse at 48% 76%,rgba(86,54,207,.14),transparent 31%),
    linear-gradient(180deg,#01030a 0%,#03152f 49%,#020611 100%)!important;
}
.hakham-cosmos:before{
  content:""!important;position:absolute!important;inset:-12%!important;opacity:.96!important;
  background:
    radial-gradient(ellipse at 75% 24%,rgba(145,204,255,.27),transparent 16%),
    radial-gradient(ellipse at 67% 33%,rgba(42,111,255,.22),transparent 27%),
    radial-gradient(ellipse at 31% 49%,rgba(0,210,255,.13),transparent 26%),
    radial-gradient(ellipse at 51% 63%,rgba(102,73,226,.11),transparent 31%)!important;
  filter:blur(19px)!important;animation:cosmicDrift 28s ease-in-out infinite alternate!important;
}
.hakham-cosmos:after{
  content:""!important;position:absolute!important;inset:auto -8vw auto auto!important;top:-18vw!important;
  width:min(58vw,920px)!important;height:min(58vw,920px)!important;border-radius:50%!important;opacity:.36!important;
  background:repeating-conic-gradient(from 12deg,rgba(180,224,255,.22) 0deg 2deg,rgba(53,113,255,.07) 3deg 7deg,transparent 8deg 15deg)!important;
  -webkit-mask-image:radial-gradient(circle,rgba(0,0,0,.96) 0 4%,rgba(0,0,0,.74) 17%,rgba(0,0,0,.28) 42%,transparent 69%)!important;
  mask-image:radial-gradient(circle,rgba(0,0,0,.96) 0 4%,rgba(0,0,0,.74) 17%,rgba(0,0,0,.28) 42%,transparent 69%)!important;
  filter:blur(9px) drop-shadow(0 0 55px rgba(85,158,255,.18))!important;animation:cosmicGalaxy 72s linear infinite!important;
}
@keyframes cosmicGalaxy{to{transform:rotate(360deg) scale(1.04)}}
.cosmic-stars{z-index:3!important}.cosmic-star{opacity:.30!important;background:#f2fdff!important;box-shadow:0 0 8px rgba(106,220,255,.88)!important}
.cosmic-star.big{opacity:.86!important;box-shadow:0 0 14px rgba(147,235,255,1),0 0 32px rgba(63,123,255,.58)!important}
.cosmic-streak{height:2px!important;filter:drop-shadow(0 0 8px #72e6ff)!important}

/* Slightly larger Hakham and cleaner fade into the reactor. */
body.contextual-ready #hakhamCore .avatar-shell{
  width:min(980px,98vw)!important;height:clamp(650px,80vh,880px)!important;padding-bottom:0!important;overflow:visible!important;
}
body.contextual-ready #hakhamCore .avatar{
  height:clamp(625px,77vh,850px)!important;max-width:min(940px,97vw)!important;object-position:center bottom!important;
  -webkit-mask-image:linear-gradient(to bottom,#000 0%,#000 70%,rgba(0,0,0,.96) 78%,rgba(0,0,0,.72) 87%,rgba(0,0,0,.24) 95%,transparent 100%)!important;
  mask-image:linear-gradient(to bottom,#000 0%,#000 70%,rgba(0,0,0,.96) 78%,rgba(0,0,0,.72) 87%,rgba(0,0,0,.24) 95%,transparent 100%)!important;
}

/* Reactor: use one vertical anchor only. top:auto prevents an older rule from fighting bottom. */
.infinity-reactor{
  left:50%!important;top:auto!important;bottom:-10.5%!important;width:min(108%,960px)!important;max-width:none!important;
  z-index:8!important;opacity:1!important;transform:translateX(-50%) scale(calc(1.01 + var(--ir-energy)*.045))!important;transform-origin:50% 50%!important;
}
.infinity-reactor .ir-track{stroke-width:13!important}.infinity-reactor .ir-halo{stroke-width:33!important}.infinity-reactor .ir-flow{stroke-width:11.5!important}.infinity-reactor .ir-pulse{stroke-width:7.2!important}

/* Natural voice health is visible again while the old synth panel stays hidden. */
.hakham-voice-health{display:inline-flex;align-items:center;min-height:30px;padding:0 9px;border:1px solid rgba(37,220,255,.25);border-radius:999px;background:rgba(4,22,36,.72);color:#8eb0c1;font-size:9px;font-weight:850;letter-spacing:.07em;white-space:nowrap}
.hakham-voice-health.ready{color:#93ffe5;border-color:rgba(39,224,173,.38);box-shadow:0 0 18px rgba(39,224,173,.08)}
.hakham-voice-health.error{color:#ffc0ca;border-color:rgba(255,100,123,.38)}

/* Contextual cards intentionally unchanged in this release. */
@media(max-width:900px){
 .hakham-cosmos{inset:58px 0 0!important}
 body.contextual-ready #hakhamCore .avatar-shell{height:clamp(485px,70vh,680px)!important}
 body.contextual-ready #hakhamCore .avatar{height:clamp(460px,67vh,650px)!important}
 .infinity-reactor{width:min(112%,760px)!important;bottom:-8.5%!important}
 .hakham-voice-health{display:none}
}
@media(max-width:520px){body.contextual-ready #hakhamCore .avatar-shell{height:445px!important}body.contextual-ready #hakhamCore .avatar{height:425px!important}.infinity-reactor{width:118%!important;bottom:-5.5%!important}}
</style>
"""


PRECISION_SCRIPT = r"""
<script id="hakham-v19-6-precision-pass-js">
(function(){
  function toastSafe(text){try{if(typeof toast==='function')toast(text)}catch(e){}}
  function voicePill(){
    let pill=document.querySelector('#hakhamVoiceHealth');if(pill)return pill;
    pill=document.createElement('span');pill.id='hakhamVoiceHealth';pill.className='hakham-voice-health';pill.textContent='VOICE · VERIFICANDO';
    const right=document.querySelector('.topright'),engine=document.querySelector('.engine');
    if(right){if(engine&&engine.parentElement===right)engine.insertAdjacentElement('afterend',pill);else right.appendChild(pill)}
    return pill;
  }
  function setVoicePill(state,label){const pill=voicePill();pill.classList.toggle('ready',state==='ready');pill.classList.toggle('error',state==='error');pill.textContent=label}

  async function forceNaturalVoice(){
    try{
      const r=await fetch('/api/status',{cache:'no-store'}),status=await r.json();if(!r.ok)throw new Error('HTTP '+r.status);
      if(!status.openai_tts_ready){setVoicePill('error','VOICE · TTS NÃO CONFIGURADO');return false}
      try{hakhamNaturalReady=true}catch(e){}try{hakhamVoiceEngine='openai'}catch(e){}
      localStorage.setItem('hakhamVoiceEngine','openai');
      try{if(typeof refreshVoiceEngineButton==='function')refreshVoiceEngineButton()}catch(e){}
      setVoicePill('ready','VOICE · '+String(status.openai_tts_voice||'CEDAR').toUpperCase());return true;
    }catch(e){setVoicePill('error','VOICE · OFFLINE');return false}
  }

  /* Prevent a TTS failure from silently switching Hakham to Windows speech. */
  try{
    if(typeof speakNatural==='function'&&typeof splitHakhamSpeech==='function'&&typeof fetchHakhamNaturalChunk==='function'&&typeof playHakhamAudio==='function'){
      speakNatural=async function(text){
        try{hakhamBrowserStop()}catch(e){}
        const chunks=splitHakhamSpeech(text);if(!chunks.length)return;
        const generation=++hakhamSpeechGeneration;try{isSpeaking=true}catch(e){}
        try{if(typeof setHakhamState==='function')setHakhamState('speaking','HAKHAM FALANDO · GPT VOICE')}catch(e){}
        try{
          let pending=fetchHakhamNaturalChunk(chunks[0],generation);
          for(let i=0;i<chunks.length;i++){const current=await pending;const next=i+1<chunks.length?fetchHakhamNaturalChunk(chunks[i+1],generation):null;await playHakhamAudio(current,generation);pending=next}
          if(generation===hakhamSpeechGeneration){try{isSpeaking=false}catch(e){};try{if(typeof setHakhamState==='function')setHakhamState('idle','PRONTO')}catch(e){};setVoicePill('ready','VOICE · CEDAR')}
        }catch(e){
          if(String(e&&e.message||e)==='speech-cancelled')return;
          try{isSpeaking=false}catch(x){};try{if(typeof setHakhamState==='function')setHakhamState('idle','PRONTO')}catch(x){}
          setVoicePill('error','VOICE · GPT INDISPONÍVEL');toastSafe('GPT Voice indisponível. Fallback de voz do Windows foi bloqueado.');
        }
      };
    }
    if(typeof speak==='function'){
      speak=function(text){
        try{if(!voiceEnabled||!text)return}catch(e){if(!text)return}
        let ready=false;try{ready=!!hakhamNaturalReady}catch(e){}
        if(ready&&typeof speakNatural==='function'){speakNatural(text);return}
        setVoicePill('error','VOICE · GPT INDISPONÍVEL');toastSafe('Voz natural indisponível. Hakham não usará a voz do Windows.');
      };
    }
  }catch(e){}

  forceNaturalVoice();setInterval(forceNaturalVoice,60000);
  setTimeout(async function(){
    try{const r=await fetch('/api/vision/recent?limit=1',{cache:'no-store'}),d=await r.json();document.body.dataset.visionReady=d&&d.configured?'true':'false';if(d&&d.model)document.body.dataset.visionModel=String(d.model)}catch(e){document.body.dataset.visionReady='false'}
  },900);
})();
</script>
"""


def _enhance(html: str) -> str:
    html = html.replace("Orbit Command v0.19.5 Cosmic Reactor", "Orbit Command v0.19.6 Precision Pass")
    html = html.replace("ORBIT COMMAND // v0.19.5 COSMIC REACTOR", "ORBIT COMMAND // v0.19.6 PRECISION PASS")
    html = html.replace("HAKHAM INFINITY ∞ v0.19.5 // SER Comtec", "HAKHAM INFINITY ∞ v0.19.6 // SER Comtec")
    html = html.replace("</head>", PRECISION_UI + "\n</head>")
    html = html.replace("</body>", PRECISION_SCRIPT + "\n</body>")
    return html


_stable_web = previous._stable_web
_stable_web.CONTROL_CENTER_HTML = _enhance(_stable_web.CONTROL_CENTER_HTML)
CONTROL_CENTER_HTML = _stable_web.CONTROL_CENTER_HTML


def main() -> None:
    import uvicorn

    uvicorn.run("hakham.web_v19_6:app", host="127.0.0.1", port=8765, reload=False)


if __name__ == "__main__":
    main()
