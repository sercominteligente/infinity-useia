from __future__ import annotations

from . import web_v19_4 as previous


app = previous.app

COSMIC_UI = r"""
<style id="hakham-v19-5-cosmic-reactor">
/* v0.19.5: cinematic cosmic hero, lower/heavier reactor and chest fade. */
body.contextual-ready{background:#010611!important}
body.contextual-ready .page,body.contextual-ready .stage{background:transparent!important}
body.contextual-ready #hakhamCore{
  position:relative!important;
  z-index:3!important;
  background:transparent!important;
  isolation:isolate!important;
}
body.contextual-ready #hakhamCore .avatar-shell{
  width:min(900px,98vw)!important;
  height:clamp(610px,78vh,820px)!important;
  overflow:visible!important;
  z-index:4!important;
}
body.contextual-ready #hakhamCore .avatar{
  height:clamp(585px,75vh,790px)!important;
  max-width:min(860px,96vw)!important;
  object-position:center bottom!important;
  filter:drop-shadow(0 0 18px rgba(46,190,255,.34)) drop-shadow(0 0 55px rgba(39,100,255,.16))!important;
  -webkit-mask-image:linear-gradient(to bottom,#000 0%,#000 66%,rgba(0,0,0,.98) 72%,rgba(0,0,0,.78) 82%,rgba(0,0,0,.30) 93%,transparent 100%)!important;
  mask-image:linear-gradient(to bottom,#000 0%,#000 66%,rgba(0,0,0,.98) 72%,rgba(0,0,0,.78) 82%,rgba(0,0,0,.30) 93%,transparent 100%)!important;
}

/* Universe backdrop lives behind every contextual card and behind Hakham. */
.hakham-cosmos{position:fixed;z-index:0;inset:64px 0 0;overflow:hidden;pointer-events:none;background:
 radial-gradient(circle at 72% 25%,rgba(119,190,255,.17) 0 1%,rgba(51,116,205,.12) 5%,transparent 22%),
 radial-gradient(ellipse at 54% 56%,rgba(0,183,255,.13),transparent 34%),
 radial-gradient(ellipse at 18% 42%,rgba(22,76,190,.18),transparent 31%),
 linear-gradient(180deg,#01040d 0%,#031128 48%,#010611 100%)}
.hakham-cosmos:before,.hakham-cosmos:after{content:"";position:absolute;inset:-15%;will-change:transform,opacity}
.hakham-cosmos:before{opacity:.46;background:
 radial-gradient(circle at 76% 22%,rgba(255,248,211,.58) 0 1px,rgba(130,188,255,.18) 3px,transparent 11%),
 radial-gradient(ellipse at 73% 27%,rgba(115,180,255,.17),transparent 9%),
 radial-gradient(ellipse at 70% 30%,rgba(54,91,189,.16),transparent 18%),
 radial-gradient(ellipse at 26% 49%,rgba(0,177,255,.11),transparent 22%);
 filter:blur(.15px);animation:cosmicDrift 34s ease-in-out infinite alternate}
.hakham-cosmos:after{opacity:.28;background:repeating-radial-gradient(circle at 50% 50%,rgba(102,216,255,.10) 0 1px,transparent 1px 18px);background-size:61px 61px;animation:cosmicParallax 46s linear infinite}
.cosmic-stars{position:absolute;inset:0;overflow:hidden}
.cosmic-star{position:absolute;width:2px;height:2px;border-radius:50%;background:#dffaff;opacity:.15;box-shadow:0 0 8px rgba(87,211,255,.8);animation:starTwinkle var(--twinkle,4s) ease-in-out infinite alternate}
.cosmic-star.big{width:3px;height:3px;box-shadow:0 0 13px rgba(73,216,255,.95),0 0 25px rgba(41,108,255,.44)}
.cosmic-streak{position:absolute;width:150px;height:1px;opacity:0;transform:rotate(-18deg);background:linear-gradient(90deg,transparent,rgba(201,246,255,.18),rgba(101,222,255,.94),transparent);filter:drop-shadow(0 0 5px #51d9ff);animation:shootingStar 1.25s ease-out forwards}
@keyframes cosmicDrift{from{transform:translate3d(-1.5%,-1%,0) scale(1.03)}to{transform:translate3d(1.8%,1.1%,0) scale(1.08)}}
@keyframes cosmicParallax{to{transform:translate3d(-42px,32px,0)}}
@keyframes starTwinkle{from{opacity:.12;transform:scale(.72)}to{opacity:.92;transform:scale(1.45)}}
@keyframes shootingStar{0%{opacity:0;transform:translate3d(-160px,-60px,0) rotate(-18deg) scaleX(.25)}18%{opacity:1}100%{opacity:0;transform:translate3d(520px,170px,0) rotate(-18deg) scaleX(1)}}

/* Make reactor the dominant chest structure instead of a thin overlay. */
.infinity-reactor{
  width:min(110%,980px)!important;
  max-width:none!important;
  bottom:-2.2%!important;
  opacity:1!important;
  z-index:8!important;
  mix-blend-mode:screen!important;
  transform:translateX(-50%) scale(calc(1.01 + var(--ir-energy)*.052))!important;
  filter:drop-shadow(0 0 calc(22px + var(--ir-energy)*38px) rgba(39,224,255,.86)) drop-shadow(0 0 calc(52px + var(--ir-energy)*58px) rgba(37,94,255,.36))!important;
}
.infinity-reactor .ir-track{stroke:#76efff!important;stroke-width:11.5!important;opacity:.82!important;filter:drop-shadow(0 0 8px #25dcff)!important}
.infinity-reactor .ir-halo{stroke:#2edfff!important;stroke-width:29!important;opacity:calc(.20 + var(--ir-energy)*.38)!important;filter:blur(8px)!important}
.infinity-reactor .ir-flow{stroke:#e4fdff!important;stroke-width:10.5!important;stroke-dasharray:6 8!important;opacity:1!important;filter:drop-shadow(0 0 5px #fff) drop-shadow(0 0 11px #25dcff)!important}
.infinity-reactor .ir-pulse{stroke:#53e8ff!important;stroke-width:6.8!important;stroke-dasharray:2 5!important;opacity:calc(.58 + var(--ir-energy)*.42)!important;filter:drop-shadow(0 0 6px #25dcff)!important}
.infinity-reactor .ir-node{r:4.5;opacity:.82!important}.infinity-reactor .ir-center{r:5.4;opacity:1!important}
#hakhamCore[data-state="idle"] .ir-flow{animation-duration:5.1s!important}
#hakhamCore[data-state="listening"] .ir-flow{stroke-width:calc(11px + var(--ir-energy)*5px)!important;animation-duration:.95s!important}
#hakhamCore[data-state="thinking"] .ir-flow{stroke-width:11.2px!important;animation-duration:1.15s!important}
#hakhamCore[data-state="speaking"] .ir-flow{stroke-width:calc(11.5px + var(--ir-energy)*8px)!important;animation-duration:.52s!important}
#hakhamCore[data-state="speaking"] .ir-halo{stroke-width:calc(29px + var(--ir-energy)*20px)!important}
#hakhamCore[data-state="executing"] .ir-flow{stroke-width:12px!important;animation-duration:.68s!important}

/* Keep contextual UI above the universe. */
body.contextual-ready .topbar{z-index:120!important}
.context-workspace{z-index:82!important}.context-minibar{z-index:105!important}
body.contextual-ready #chatPanel{z-index:130!important}
.hakham-caption{z-index:129!important}

@media(max-width:900px){
 .hakham-cosmos{inset:58px 0 0}
 body.contextual-ready #hakhamCore .avatar-shell{height:clamp(455px,68vh,650px)!important}
 body.contextual-ready #hakhamCore .avatar{height:clamp(430px,65vh,625px)!important}
 .infinity-reactor{width:min(111%,720px)!important;bottom:-1.4%!important}
 .infinity-reactor .ir-track{stroke-width:10!important}.infinity-reactor .ir-halo{stroke-width:24!important}.infinity-reactor .ir-flow{stroke-width:9!important}.infinity-reactor .ir-pulse{stroke-width:5.5!important}
}
@media(max-width:520px){
 body.contextual-ready #hakhamCore .avatar-shell{height:430px!important}
 body.contextual-ready #hakhamCore .avatar{height:415px!important}
 .infinity-reactor{width:116%!important;bottom:0!important}
 .infinity-reactor .ir-track{stroke-width:9!important}.infinity-reactor .ir-halo{stroke-width:21!important}.infinity-reactor .ir-flow{stroke-width:8.2!important}.infinity-reactor .ir-pulse{stroke-width:5!important}
}
@media(prefers-reduced-motion:reduce){.hakham-cosmos:before,.hakham-cosmos:after,.cosmic-star{animation:none!important}.cosmic-streak{display:none!important}}
</style>
"""

COSMIC_SHELL = r"""
<div class="hakham-cosmos" id="hakhamCosmos" aria-hidden="true"><div class="cosmic-stars" id="cosmicStars"></div></div>
"""

COSMIC_SCRIPT = r"""
<script id="hakham-v19-5-cosmic-reactor-js">
(function(){
  const cosmos=document.querySelector('#hakhamCosmos');
  const stars=document.querySelector('#cosmicStars');
  if(!cosmos||!stars)return;
  let seed=1905;
  function rnd(){seed=(seed*1664525+1013904223)>>>0;return seed/4294967296}
  const count=window.innerWidth<700?54:105;
  for(let i=0;i<count;i++){
    const s=document.createElement('i');s.className='cosmic-star'+(i%13===0?' big':'');
    s.style.left=(rnd()*100).toFixed(2)+'%';s.style.top=(rnd()*100).toFixed(2)+'%';
    s.style.setProperty('--twinkle',(2.2+rnd()*5.8).toFixed(2)+'s');s.style.animationDelay=(-rnd()*7).toFixed(2)+'s';stars.appendChild(s)
  }
  function streak(){
    if(document.hidden||window.matchMedia('(prefers-reduced-motion: reduce)').matches)return;
    const s=document.createElement('i');s.className='cosmic-streak';
    s.style.left=(-8+rnd()*42)+'%';s.style.top=(5+rnd()*58)+'%';s.style.animationDuration=(.92+rnd()*.75).toFixed(2)+'s';stars.appendChild(s);
    setTimeout(function(){s.remove()},2100)
  }
  setTimeout(streak,2400);setInterval(function(){if(rnd()>.38)streak()},6100);
})();
</script>
"""


def _enhance(html: str) -> str:
    html = html.replace("Orbit Command v0.19.4 Reactor Fusion", "Orbit Command v0.19.5 Cosmic Reactor")
    html = html.replace("ORBIT COMMAND // v0.19.4 REACTOR FUSION", "ORBIT COMMAND // v0.19.5 COSMIC REACTOR")
    html = html.replace("HAKHAM INFINITY ∞ v0.19.4 // SER Comtec", "HAKHAM INFINITY ∞ v0.19.5 // SER Comtec")
    html = html.replace("</head>", COSMIC_UI + "\n</head>")
    html = html.replace("<body>", "<body>\n" + COSMIC_SHELL, 1)
    html = html.replace("</body>", COSMIC_SCRIPT + "\n</body>")
    return html


_stable_web = previous._stable_web
_stable_web.CONTROL_CENTER_HTML = _enhance(_stable_web.CONTROL_CENTER_HTML)
CONTROL_CENTER_HTML = _stable_web.CONTROL_CENTER_HTML


def main() -> None:
    import uvicorn

    uvicorn.run("hakham.web_v19_5:app", host="127.0.0.1", port=8765, reload=False)


if __name__ == "__main__":
    main()
