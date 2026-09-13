from __future__ import annotations

from . import web_v19 as previous


app = previous.app

REACTOR_UI = r"""
<style id="hakham-v19-1-infinity-reactor">
.infinity-reactor{--ir-energy:.12;--ir-scale:1;position:absolute;z-index:5;left:50%;bottom:-2px;width:min(590px,82vw);height:220px;transform:translateX(-50%) scale(var(--ir-scale));transform-origin:50% 55%;pointer-events:none;filter:drop-shadow(0 0 calc(12px + var(--ir-energy)*30px) rgba(37,220,255,.32));transition:filter .22s ease}
.infinity-reactor svg{display:block;width:100%;height:100%;overflow:visible}
.ir-shadow{fill:none;stroke:#020a13;stroke-width:18;opacity:.72}
.ir-halo{fill:none;stroke:#25dcff;stroke-width:13;opacity:calc(.08 + var(--ir-energy)*.20);filter:blur(8px)}
.ir-track{fill:none;stroke:rgba(123,226,255,.24);stroke-width:3.2;stroke-linecap:round;stroke-linejoin:round}
.ir-flow,.ir-pulse{fill:none;stroke-linecap:round;stroke-linejoin:round;vector-effect:non-scaling-stroke}
.ir-flow{stroke:#25dcff;stroke-width:4.2;stroke-dasharray:17 83;filter:drop-shadow(0 0 7px rgba(37,220,255,.95));animation:irTravel 5.8s linear infinite}
.ir-pulse{stroke:#f4b75b;stroke-width:2;stroke-dasharray:3 10;opacity:calc(.18 + var(--ir-energy)*.65);filter:drop-shadow(0 0 7px rgba(244,183,91,.65));animation:irTravelBack 8.5s linear infinite}
.ir-node{fill:#c9f8ff;opacity:.42;filter:drop-shadow(0 0 6px #25dcff)}
.ir-center{fill:#effcff;opacity:calc(.42 + var(--ir-energy)*.50);filter:drop-shadow(0 0 10px #25dcff)}
.ir-state{position:absolute;left:50%;bottom:0;transform:translateX(-50%);white-space:nowrap;font-size:9px;font-weight:900;letter-spacing:.18em;color:rgba(173,226,243,.68);text-shadow:0 0 12px rgba(37,220,255,.5)}
@keyframes irTravel{to{stroke-dashoffset:-100}}@keyframes irTravelBack{to{stroke-dashoffset:100}}
#hakhamCore[data-state="idle"] .ir-flow{animation-duration:7.2s;opacity:.58}
#hakhamCore[data-state="idle"] .ir-pulse{animation-duration:10s}
#hakhamCore[data-state="listening"] .infinity-reactor{filter:drop-shadow(0 0 calc(18px + var(--ir-energy)*36px) rgba(39,224,173,.48))}
#hakhamCore[data-state="listening"] .ir-halo,#hakhamCore[data-state="listening"] .ir-flow{stroke:#27e0ad}
#hakhamCore[data-state="listening"] .ir-flow{animation-duration:1.55s;stroke-dasharray:10 16;opacity:.95}
#hakhamCore[data-state="listening"] .ir-pulse{stroke:#8df4ff;animation-duration:2.4s;opacity:.72}
#hakhamCore[data-state="thinking"] .infinity-reactor{filter:drop-shadow(0 0 calc(17px + var(--ir-energy)*31px) rgba(154,112,255,.42))}
#hakhamCore[data-state="thinking"] .ir-halo,#hakhamCore[data-state="thinking"] .ir-flow{stroke:#9a70ff}
#hakhamCore[data-state="thinking"] .ir-flow{animation-duration:1.9s;stroke-dasharray:7 11;opacity:.9}
#hakhamCore[data-state="thinking"] .ir-pulse{stroke:#25dcff;animation-duration:3.1s;opacity:.66}
#hakhamCore[data-state="speaking"] .infinity-reactor{filter:drop-shadow(0 0 calc(21px + var(--ir-energy)*42px) rgba(37,220,255,.60))}
#hakhamCore[data-state="speaking"] .ir-flow{stroke:#25dcff;animation-duration:.92s;stroke-dasharray:5 8;opacity:1}
#hakhamCore[data-state="speaking"] .ir-pulse{stroke:#f4b75b;animation-duration:1.35s;stroke-width:calc(2px + var(--ir-energy)*3px);opacity:.92}
#hakhamCore[data-state="executing"] .ir-flow{stroke:#f4b75b;animation-duration:1.25s;stroke-dasharray:12 10;opacity:.94}
#hakhamCore[data-state="executing"] .ir-pulse{stroke:#25dcff;animation-duration:1.8s;opacity:.78}
body.contextual-ready #hakhamCore .avatar-shell{padding-bottom:48px}
body.contextual-ready #hakhamCore .avatar{transform-origin:50% 67%}
@media(max-width:900px){.infinity-reactor{width:min(520px,91vw);height:190px;bottom:-4px}.ir-state{font-size:8px;bottom:-1px}}
@media(max-width:520px){.infinity-reactor{width:94vw;height:168px;bottom:-8px}body.contextual-ready #hakhamCore .avatar-shell{padding-bottom:34px}}
</style>
"""

REACTOR_SCRIPT = r"""
<script id="hakham-v19-1-infinity-reactor-js">
(function(){
  const core=document.querySelector('#hakhamCore');
  const shell=core&&core.querySelector('.avatar-shell');
  if(!core||!shell||shell.querySelector('#infinityReactor'))return;

  const reactor=document.createElement('div');
  reactor.className='infinity-reactor';
  reactor.id='infinityReactor';
  reactor.setAttribute('aria-label','Infinity Reactor');
  reactor.innerHTML='<svg viewBox="0 0 360 190" role="img" aria-hidden="true"><path class="ir-shadow" pathLength="100" d="M36 95 C36 41 91 35 137 85 C155 105 166 119 180 119 C194 119 205 105 223 85 C269 35 324 41 324 95 C324 149 269 155 223 105 C205 85 194 71 180 71 C166 71 155 85 137 105 C91 155 36 149 36 95"/><path class="ir-halo" pathLength="100" d="M36 95 C36 41 91 35 137 85 C155 105 166 119 180 119 C194 119 205 105 223 85 C269 35 324 41 324 95 C324 149 269 155 223 105 C205 85 194 71 180 71 C166 71 155 85 137 105 C91 155 36 149 36 95"/><path class="ir-track" pathLength="100" d="M36 95 C36 41 91 35 137 85 C155 105 166 119 180 119 C194 119 205 105 223 85 C269 35 324 41 324 95 C324 149 269 155 223 105 C205 85 194 71 180 71 C166 71 155 85 137 105 C91 155 36 149 36 95"/><path class="ir-flow" pathLength="100" d="M36 95 C36 41 91 35 137 85 C155 105 166 119 180 119 C194 119 205 105 223 85 C269 35 324 41 324 95 C324 149 269 155 223 105 C205 85 194 71 180 71 C166 71 155 85 137 105 C91 155 36 149 36 95"/><path class="ir-pulse" pathLength="100" d="M36 95 C36 41 91 35 137 85 C155 105 166 119 180 119 C194 119 205 105 223 85 C269 35 324 41 324 95 C324 149 269 155 223 105 C205 85 194 71 180 71 C166 71 155 85 137 105 C91 155 36 149 36 95"/><circle class="ir-node" cx="36" cy="95" r="3"/><circle class="ir-node" cx="324" cy="95" r="3"/><circle class="ir-center" cx="180" cy="95" r="3.4"/></svg><div class="ir-state" id="infinityReactorState">INFINITY REACTOR // PRONTO</div>';
  shell.appendChild(reactor);

  const flow=reactor.querySelector('.ir-flow');
  const pulse=reactor.querySelector('.ir-pulse');
  const halo=reactor.querySelector('.ir-halo');
  const stateLabel=reactor.querySelector('#infinityReactorState');
  let bins=null;
  let syntheticPhase=0;

  function stateName(){return core.dataset.state||'idle'}
  function labelFor(state){return({idle:'PRONTO',listening:'OUVINDO',thinking:'PENSANDO',speaking:'FALANDO',executing:'EXECUTANDO'}[state]||String(state).toUpperCase())}
  function updateLabel(){stateLabel.textContent='INFINITY REACTOR // '+labelFor(stateName())}
  new MutationObserver(updateLabel).observe(core,{attributes:true,attributeFilter:['data-state']});
  updateLabel();

  function audioEnergy(){
    try{
      if(typeof analyser!=='undefined'&&analyser){
        if(!bins||bins.length!==analyser.frequencyBinCount)bins=new Uint8Array(analyser.frequencyBinCount);
        analyser.getByteFrequencyData(bins);
        let total=0,peak=0;for(let i=0;i<bins.length;i++){total+=bins[i];if(bins[i]>peak)peak=bins[i]}
        return Math.min(1,((total/Math.max(1,bins.length))/255)*1.4+(peak/255)*.32);
      }
    }catch(e){}
    const state=stateName();syntheticPhase+=.055;
    if(state==='speaking')return .30+.18*(.5+.5*Math.sin(syntheticPhase*4.2));
    if(state==='listening')return .24+.16*(.5+.5*Math.sin(syntheticPhase*3.5));
    if(state==='thinking')return .18+.11*(.5+.5*Math.sin(syntheticPhase*1.9));
    if(state==='executing')return .22+.12*(.5+.5*Math.sin(syntheticPhase*2.6));
    return .08+.035*(.5+.5*Math.sin(syntheticPhase));
  }

  function tick(){
    const energy=audioEnergy();
    reactor.style.setProperty('--ir-energy',energy.toFixed(3));
    reactor.style.setProperty('--ir-scale',(1+energy*.045).toFixed(4));
    flow.style.strokeWidth=(3.6+energy*7.5).toFixed(2);
    halo.style.strokeWidth=(10+energy*12).toFixed(2);
    pulse.style.strokeDashoffset=String(-(performance.now()/45)*(1+energy*2.4));
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
})();
</script>
"""


def _enhance(html: str) -> str:
    html = html.replace("Orbit Command v0.19 Contextual Workspace", "Orbit Command v0.19.1 Infinity Reactor")
    html = html.replace("ORBIT COMMAND // v0.19 CONTEXTUAL WORKSPACE", "ORBIT COMMAND // v0.19.1 INFINITY REACTOR")
    html = html.replace("HAKHAM INFINITY ∞ v0.19 // SER Comtec", "HAKHAM INFINITY ∞ v0.19.1 // SER Comtec")
    html = html.replace("</head>", REACTOR_UI + "\n</head>")
    html = html.replace("</body>", REACTOR_SCRIPT + "\n</body>")
    return html


_stable_web = previous._stable_web
_stable_web.CONTROL_CENTER_HTML = _enhance(_stable_web.CONTROL_CENTER_HTML)
CONTROL_CENTER_HTML = _stable_web.CONTROL_CENTER_HTML


def main() -> None:
    import uvicorn

    uvicorn.run("hakham.web_v19_1:app", host="127.0.0.1", port=8765, reload=False)


if __name__ == "__main__":
    main()
