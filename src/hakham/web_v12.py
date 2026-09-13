from __future__ import annotations

from . import web_v11 as research_layer
from . import web_v8


app = research_layer.app

PRIVACY_UI = r"""
<style id="hakham-v12-privacy">
#memoryPanel{display:none!important}
.memory-nav-hidden{display:none!important}
</style>
"""

PRIVACY_SCRIPT = r"""
<script id="hakham-v12-privacy-js">
(function(){
  document.querySelectorAll('.menu button').forEach(function(button){
    if((button.textContent||'').trim().toUpperCase()==='MEMÓRIA'){
      button.classList.add('memory-nav-hidden');
      button.removeAttribute('onclick');
    }
  });
  const search=document.querySelector('#globalSearch');
  if(search){
    search.placeholder='Pergunte ao Hakham...';
    search.addEventListener('keydown',function(event){
      if(event.key!=='Enter')return;
      event.preventDefault();
      event.stopImmediatePropagation();
      const input=document.querySelector('#chatInput');
      if(!input)return;
      input.value=search.value.trim();
      search.value='';
      const panel=document.querySelector('#chatPanel');if(panel)panel.scrollIntoView({behavior:'smooth'});
      input.focus();
    },true);
  }
})();
</script>
"""


def _enhance(html: str) -> str:
    html = html.replace("Orbit Command v0.11 Research", "Orbit Command v0.12 Stable Demo")
    html = html.replace("ORBIT COMMAND // v0.11 RESEARCH", "ORBIT COMMAND // v0.12 STABLE DEMO")
    html = html.replace("HAKHAM INFINITY ∞ v0.11 // SER Comtec", "HAKHAM INFINITY ∞ v0.12 // SER Comtec")
    html = html.replace("</head>", PRIVACY_UI + "\n</head>")
    html = html.replace("</body>", PRIVACY_SCRIPT + "\n</body>")
    return html


web_v8.CONTROL_CENTER_HTML = _enhance(web_v8.CONTROL_CENTER_HTML)
CONTROL_CENTER_HTML = web_v8.CONTROL_CENTER_HTML


def main() -> None:
    import uvicorn

    uvicorn.run("hakham.web_v12:app", host="127.0.0.1", port=8765, reload=False)


if __name__ == "__main__":
    main()
