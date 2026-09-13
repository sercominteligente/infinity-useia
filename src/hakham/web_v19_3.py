from __future__ import annotations

from . import web_v19_2 as previous
from . import web_research


app = previous.app

# v0.19.3 broadens the existing read-only web research trigger so natural
# requests for current news do not depend on the LLM guessing whether browsing
# is available. WebResearchService already performs the actual search and has a
# no-key DuckDuckGo fallback when Abacus search is unavailable.
_EXTRA_WEB_INTENTS = (
    "notícia",
    "noticia",
    "notícias",
    "noticias",
    "manchete",
    "manchetes",
    "mercado financeiro",
    "ibovespa",
    "bolsa de valores",
    "cotação",
    "cotacao",
    "dólar hoje",
    "dolar hoje",
    "esporte",
    "esportes",
    "futebol",
    "copa",
    "no google",
    "no Google",
)
web_research.WEB_INTENT_MARKERS = tuple(
    dict.fromkeys((*web_research.WEB_INTENT_MARKERS, *_EXTRA_WEB_INTENTS))
)


CONTROL_UI = r"""
<style id="hakham-v19-3-contextual-control">
.context-window.cw-closing{animation:cwClose .16s ease forwards!important;pointer-events:none!important}
@keyframes cwClose{to{opacity:0;transform:translateY(10px) scale(.975)}}
</style>
"""

CONTROL_SCRIPT = r"""
<script id="hakham-v19-3-contextual-control-js">
(function(){
  const input=document.querySelector('#chatInput');
  const sendButton=document.querySelector('#sendBtn');
  if(!input||!sendButton)return;

  const previousSend=typeof window.sendChat==='function'?window.sendChat:null;
  const aliases={
    research:['notícia','noticia','notícias','noticias','pesquisa','research','manchete','manchetes','esporte','esportes','futebol','mercado financeiro'],
    instagram:['instagram','insta'],
    agents:['agente','agentes','conselho'],
    tools:['ferramenta','ferramentas','tool','tools','tool gateway'],
    status:['status','sistema','runtime'],
    projects:['projeto','projetos'],
    memory:['memória','memoria','memórias','memorias'],
    whatsapp:['whatsapp','whats'],
    commercial:['orçamento','orcamento','proposta','commercial','comercial'],
    drive:['drive','google drive'],
    github:['github','repositório','repositorio'],
    webcam:['webcam','câmera','camera','visão','visao'],
    email:['e-mail','email'],
  };

  function clean(value){return String(value||'').replace(/\s+/g,' ').trim()}
  function closeIntent(text){
    const raw=clean(text),low=raw.toLocaleLowerCase('pt-BR');
    if(!/\b(fechar|feche|fecha|fechem|encerre|encerrar|dispense|remova|remover)\b/i.test(low))return null;
    if(/\b(todos|todas|tudo)\b/i.test(low)&&/\b(cards?|janelas?|pain[eé]is?)\b/i.test(low))return{all:true,label:'todos os cards'};
    if(/\b(fechar|feche|fecha)\s+(todos|todas|tudo)\b/i.test(low))return{all:true,label:'todos os cards'};
    for(const kind of Object.keys(aliases)){
      if(aliases[kind].some(function(alias){return low.indexOf(alias)>=0}))return{kind:kind,label:aliases[kind][0]};
    }
    if(/\b(cards?|janelas?|pain[eé]is?)\b/i.test(low))return{active:true,label:'card ativo'};
    return null;
  }

  function visibleWindows(){return Array.from(document.querySelectorAll('.context-window')).filter(function(win){return win.isConnected&&!win.classList.contains('minimized')})}

  function announce(text){
    try{if(typeof addBubble==='function')addBubble('HAKHAM',text)}catch(e){}
    const caption=document.querySelector('#hakhamCaption');
    if(caption){caption.textContent=text;caption.classList.add('show');clearTimeout(caption._v193hide);caption._v193hide=setTimeout(function(){caption.classList.remove('show')},5000)}
    try{if(typeof voiceEnabled==='undefined'||voiceEnabled){if(typeof speakHakham==='function')speakHakham(text)}}catch(e){}
  }

  function closeOne(win){
    if(!win)return false;
    const button=win.querySelector('[data-close]');
    win.classList.add('cw-closing');
    setTimeout(function(){
      if(button&&button.isConnected)button.click();
      else if(win.isConnected)win.remove();
    },135);
    return true;
  }

  function closeByIntent(intent){
    const wins=visibleWindows();
    if(!wins.length){announce('Não há nenhum card aberto, Ach.');return true}
    if(intent.all){wins.forEach(closeOne);announce('Fechando todos os cards, Ach.');return true}
    let target=null;
    if(intent.kind)target=wins.slice().reverse().find(function(win){return win.dataset.kind===intent.kind})||null;
    if(!target&&intent.active)target=wins[wins.length-1]||null;
    if(!target){announce('Esse card não está aberto no momento, Ach.');return true}
    const title=(target.querySelector('.cw-title b')||{}).textContent||intent.label||'card';
    closeOne(target);announce('Fechando '+title+', Ach.');return true
  }

  async function v193Send(){
    const text=clean(input.value);if(!text)return;
    const intent=closeIntent(text);
    if(intent){input.value='';try{if(typeof addBubble==='function')addBubble('ACH',text)}catch(e){};try{if(typeof setState==='function')setState('executing','FECHANDO CARD')}catch(e){};closeByIntent(intent);setTimeout(function(){try{if(typeof setState==='function')setState('idle')}catch(e){}},220);return}
    if(previousSend)return previousSend();
  }

  window.sendChat=v193Send;try{sendChat=v193Send}catch(e){}
  sendButton.onclick=v193Send;
  input.addEventListener('keydown',function(event){
    if(event.key!=='Enter'||event.shiftKey)return;
    if(!closeIntent(input.value))return;
    event.preventDefault();event.stopImmediatePropagation();v193Send();
  },true);
})();
</script>
"""


def _enhance(html: str) -> str:
    html = html.replace("Orbit Command v0.19.2 Embedded Reactor", "Orbit Command v0.19.3 Context Controls")
    html = html.replace("ORBIT COMMAND // v0.19.2 EMBEDDED REACTOR", "ORBIT COMMAND // v0.19.3 CONTEXT CONTROLS")
    html = html.replace("HAKHAM INFINITY ∞ v0.19.2 // SER Comtec", "HAKHAM INFINITY ∞ v0.19.3 // SER Comtec")
    html = html.replace("</head>", CONTROL_UI + "\n</head>")
    html = html.replace("</body>", CONTROL_SCRIPT + "\n</body>")
    return html


_stable_web = previous._stable_web
_stable_web.CONTROL_CENTER_HTML = _enhance(_stable_web.CONTROL_CENTER_HTML)
CONTROL_CENTER_HTML = _stable_web.CONTROL_CENTER_HTML


def main() -> None:
    import uvicorn

    uvicorn.run("hakham.web_v19_3:app", host="127.0.0.1", port=8765, reload=False)


if __name__ == "__main__":
    main()
