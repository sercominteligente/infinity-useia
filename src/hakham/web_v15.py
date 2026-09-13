from __future__ import annotations

from . import web_v14 as commercial_layer


app = commercial_layer.app

OPEN_CORE_UI = r"""
<style id="hakham-v15-open-core">
/* v0.15 Open Core: Hakham dominates the center, sidecards hug the edges,
   chat + WhatsApp become the primary operational surface below the core.
   Voice scope canvas and avatar state animations remain untouched. */
.page{width:100%;max-width:none;margin:0;padding:14px clamp(10px,1vw,20px) 34px}
.stage{
  display:grid;
  grid-template-columns:minmax(250px,.62fr) minmax(650px,1.58fr) minmax(300px,.72fr);
  grid-template-areas:
    "left core right"
    "left chat chat";
  row-gap:16px;
  column-gap:clamp(22px,1.55vw,32px);
  align-items:start;
}
.stage>.left{grid-area:left;align-self:stretch}
.stage>#hakhamCore{grid-area:core}
.stage>.right{grid-area:right}
.stage>#chatPanel{grid-area:chat}

/* Open the central chamber without removing the visual anchoring. */
#hakhamCore{
  border:0!important;
  border-radius:0!important;
  box-shadow:none!important;
  backdrop-filter:none!important;
  overflow:visible!important;
  min-height:760px;
  padding:12px clamp(20px,2.1vw,42px) 16px;
  background:
    radial-gradient(circle at 50% 38%,rgba(17,177,235,.20),transparent 29%),
    radial-gradient(ellipse at 50% 72%,rgba(23,111,196,.08),transparent 42%)!important;
}
#hakhamCore:before{display:none!important}
#hakhamCore .core-title{margin-top:3px}
#hakhamCore .core-title h1{font-size:clamp(30px,2vw,39px)}
#hakhamCore .core-title p{font-size:14px;max-width:760px;margin-inline:auto}
#hakhamCore .avatar-shell{width:min(780px,100%);height:535px;margin-top:2px}
#hakhamCore .avatar{height:min(525px,31vw);max-height:525px;max-width:100%}
#hakhamCore .orbit{width:465px;height:465px}
#hakhamCore .energy-disc{width:390px;height:105px}
#hakhamCore .state{right:clamp(12px,3vw,48px);top:14px}

/* Keep the decoder prominent and fluid while Hakham speaks. */
#hakhamCore .synth{width:min(940px,100%);margin-top:-2px}
#hakhamCore .scope{height:138px}
#hakhamCore .scope canvas{width:100%;height:100%;display:block}
#hakhamCore .voice-controls{margin-top:11px}

/* Side columns become compact control towers, firmly anchored to the edges. */
.stage>.left,.stage>.right{gap:14px;min-width:0}
.stage>.left{justify-self:stretch}
.stage>.right{justify-self:stretch}
.stage>.left .panel,.stage>.right .panel{padding:15px 16px}
.stage>.left .panel-head,.stage>.right .panel-head{margin-bottom:10px}
.stage>.left .row,.stage>.right .row{padding:8px 9px}
#toolsPanel .tool-grid{max-height:430px}

/* The operational chat is now deliberately large and sits below Hakham. */
#chatPanel{
  margin-top:0!important;
  min-height:560px;
  padding:18px 20px 20px;
  border-radius:16px;
  background:linear-gradient(145deg,rgba(5,20,36,.82),rgba(2,10,18,.72));
}
#chatPanel .chatlog{height:clamp(350px,38vh,520px);padding:6px 7px 14px}
#chatPanel .bubble{max-width:min(1120px,88%);font-size:15px;line-height:1.58}
#chatPanel .compose textarea{min-height:96px;max-height:260px;font-size:16px}
#chatPanel .wabar{padding:11px 12px;margin-bottom:10px}
#chatPanel .visionbar{padding:10px 12px;margin-bottom:10px}
#chatPanel .chat-head{margin-bottom:13px}
#chatPanel .chat-head h2{font-size:18px}

/* Wide desktop: cards hug the physical edges while the core gets a clean moat. */
@media(min-width:1700px){
  .page{padding-left:8px;padding-right:8px}
  .stage{
    grid-template-columns:minmax(270px,.58fr) minmax(780px,1.75fr) minmax(320px,.68fr);
    row-gap:18px;
    column-gap:clamp(28px,1.7vw,38px);
  }
  #hakhamCore{min-height:790px;padding-left:42px;padding-right:42px}
  #hakhamCore .avatar-shell{height:560px}
  #hakhamCore .avatar{height:550px;max-height:550px}
  #hakhamCore .orbit{width:490px;height:490px}
  #chatPanel .chatlog{height:460px}
}

/* Notebook: preserve the open-core idea without crushing side cards. */
@media(max-width:1350px){
  .stage{
    grid-template-columns:minmax(0,1fr) minmax(0,1fr);
    grid-template-areas:
      "core core"
      "chat chat"
      "left right";
    column-gap:16px;
  }
  #hakhamCore{min-height:720px;padding-left:18px;padding-right:18px}
  #hakhamCore .avatar-shell{height:485px}
  #hakhamCore .avatar{height:470px;max-height:470px;max-width:min(720px,94vw)}
  #hakhamCore .orbit{width:420px;height:420px}
  #chatPanel{min-height:540px}
  #chatPanel .chatlog{height:360px}
}

@media(max-width:900px){
  .stage{
    display:grid!important;
    grid-template-columns:1fr;
    grid-template-areas:"core" "chat" "left" "right";
    gap:14px;
  }
  .stage>.left,.stage>.right{display:grid;grid-template-columns:1fr 1fr;gap:12px;width:100%}
  .stage>.left>#projectsPanel,.stage>.left>#toolsPanel,.stage>.right>#agentsPanel{grid-column:1/-1}
  #hakhamCore{min-height:660px;padding:12px 8px 14px}
  #hakhamCore .avatar-shell{height:430px}
  #hakhamCore .avatar{height:415px;max-height:415px;max-width:94vw}
  #hakhamCore .orbit{width:355px;height:355px}
  #hakhamCore .synth{width:100%}
  #hakhamCore .scope{height:118px}
  #chatPanel{min-height:520px}
  #chatPanel .chatlog{height:330px}
}

@media(max-width:640px){
  .page{padding:8px}
  .stage>.left,.stage>.right{grid-template-columns:1fr}
  .stage>.left>#projectsPanel,.stage>.left>#toolsPanel,.stage>.right>#agentsPanel{grid-column:auto}
  #hakhamCore{min-height:585px;padding:10px 4px 12px}
  #hakhamCore .core-title h1{font-size:clamp(25px,8vw,34px)}
  #hakhamCore .avatar-shell{height:330px}
  #hakhamCore .avatar{height:315px;max-height:315px;max-width:97vw}
  #hakhamCore .orbit{width:265px;height:265px}
  #hakhamCore .energy-disc{width:270px;height:76px}
  #hakhamCore .scope{height:100px}
  #chatPanel{min-height:560px;padding:14px 11px 16px}
  #chatPanel .chatlog{height:320px}
  #chatPanel .bubble{max-width:100%}
  #chatPanel .compose textarea{min-height:92px}
}
</style>
"""

OPEN_CORE_SCRIPT = r"""
<script id="hakham-v15-open-core-js">
(function(){
  function polishCoreStatus(){
    const badge=document.querySelector('#systemBadge');
    const list=document.querySelector('#statusList');
    if(!badge||!list)return;
    const rows=Array.from(list.querySelectorAll('.statusline'));
    const coreRow=rows.find(function(row){
      const first=row.querySelector('span');
      return first&&first.textContent.trim()==='Core';
    });
    if(!coreRow)return;
    const value=coreRow.querySelector('span:last-child');
    if(value&&value.textContent.trim()==='STANDBY'&&badge.textContent.trim()==='OPERACIONAL'){
      value.textContent='PRONTO';
      value.title='Runtime carregado sob demanda';
    }
  }

  function installOpenCore(){
    const stage=document.querySelector('.stage');
    const left=document.querySelector('.stage > .left');
    const right=document.querySelector('.stage > .right');
    const chat=document.querySelector('#chatPanel');
    const tools=document.querySelector('#toolsPanel');
    if(!stage||!left||!right||!chat)return;

    /* Moving a live DOM node preserves event listeners, canvas state and the
       WebAudio analyser. The voice decoder therefore keeps running untouched. */
    if(chat.parentElement!==stage)stage.appendChild(chat);
    if(tools&&tools.parentElement!==left)left.appendChild(tools);

    stage.classList.add('open-core-stage');
    document.body.classList.add('open-core-ready');

    /* Force one layout pass only. Do not recreate/replace voiceScope canvas. */
    requestAnimationFrame(function(){
      const scope=document.querySelector('#voiceScope');
      if(scope){scope.style.width='100%';scope.style.height='100%'}
      polishCoreStatus();
    });

    const statusList=document.querySelector('#statusList');
    if(statusList){
      new MutationObserver(polishCoreStatus).observe(statusList,{childList:true,subtree:true,characterData:true});
    }
  }

  if(document.readyState==='loading'){
    document.addEventListener('DOMContentLoaded',installOpenCore,{once:true});
  }else{
    installOpenCore();
  }
})();
</script>
"""


def _enhance(html: str) -> str:
    html = html.replace("Orbit Command v0.14 Commercial Core", "Orbit Command v0.15 Open Core")
    html = html.replace("ORBIT COMMAND // v0.14 COMMERCIAL CORE", "ORBIT COMMAND // v0.15 OPEN CORE")
    html = html.replace("HAKHAM INFINITY ∞ v0.14 // SER Comtec", "HAKHAM INFINITY ∞ v0.15 // SER Comtec")
    html = html.replace("</head>", OPEN_CORE_UI + "\n</head>")
    html = html.replace("</body>", OPEN_CORE_SCRIPT + "\n</body>")
    return html


commercial_layer.reliable_layer.stable_layer.web_v8.CONTROL_CENTER_HTML = _enhance(
    commercial_layer.reliable_layer.stable_layer.web_v8.CONTROL_CENTER_HTML
)
CONTROL_CENTER_HTML = commercial_layer.reliable_layer.stable_layer.web_v8.CONTROL_CENTER_HTML


def main() -> None:
    import uvicorn

    uvicorn.run("hakham.web_v15:app", host="127.0.0.1", port=8765, reload=False)


if __name__ == "__main__":
    main()
