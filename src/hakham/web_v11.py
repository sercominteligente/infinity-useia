from __future__ import annotations

from . import web_v10 as demo_layer


app = demo_layer.app

RESEARCH_UI = r"""
<style id="hakham-v11-research">
.research-chip{display:inline-flex;align-items:center;gap:6px;margin-right:10px;padding:4px 9px;border:1px solid rgba(39,224,173,.32);border-radius:999px;background:rgba(4,38,35,.62);color:#69f0c4;font-size:11px;font-weight:800;letter-spacing:.05em;white-space:nowrap}
.research-chip:before{content:"";width:7px;height:7px;border-radius:50%;background:#27e0ad;box-shadow:0 0 11px #27e0ad}
.chat-runtime{display:flex;align-items:center;justify-content:flex-end;gap:4px;flex-wrap:wrap}
@media(max-width:640px){.chat-runtime{justify-content:flex-start}.research-chip{font-size:10px;margin-right:4px}}
</style>
"""

RESEARCH_SCRIPT = r"""
<script id="hakham-v11-research-js">
(function(){
  const hint='Pesquise na internet: ';
  document.addEventListener('click',function(event){
    const tile=event.target.closest&&event.target.closest('[data-tool="web.search"]');
    if(!tile)return;
    event.preventDefault();
    event.stopImmediatePropagation();
    const input=document.querySelector('#chatInput');
    if(!input)return;
    if(!input.value.trim())input.value=hint;
    else if(!input.value.toLowerCase().includes('pesquise'))input.value=hint+input.value.trim();
    input.focus();
    const panel=document.querySelector('#chatPanel');if(panel)panel.scrollIntoView({behavior:'smooth'});
    if(typeof toast==='function')toast('Pesquisa Web pronta · descreva a empresa ou cole o site/perfil');
  },true);
})();
</script>
"""


def _enhance(html: str) -> str:
    html = html.replace("Orbit Command v0.10 Demo", "Orbit Command v0.11 Research")
    html = html.replace("ORBIT COMMAND // v0.10 DEMO", "ORBIT COMMAND // v0.11 RESEARCH")
    html = html.replace("HAKHAM INFINITY ∞ v0.10 // SER Comtec", "HAKHAM INFINITY ∞ v0.11 // SER Comtec")
    html = html.replace("</head>", RESEARCH_UI + "\n</head>")
    old = '<div class="chat-head"><h2>CHAT COM HAKHAM</h2><span id="chatEngine">'
    new = '<div class="chat-head"><h2>CHAT COM HAKHAM</h2><div class="chat-runtime"><span class="research-chip">WEB RESEARCH</span><span id="chatEngine">'
    html = html.replace(old, new, 1)
    html = html.replace('</span></div><div class="chatlog" id="chatLog">', '</span></div></div><div class="chatlog" id="chatLog">', 1)
    html = html.replace("</body>", RESEARCH_SCRIPT + "\n</body>")
    return html


demo_layer.vision_layer.previous.CONTROL_CENTER_HTML = _enhance(
    demo_layer.vision_layer.previous.CONTROL_CENTER_HTML
)
CONTROL_CENTER_HTML = demo_layer.vision_layer.previous.CONTROL_CENTER_HTML


def main() -> None:
    import uvicorn

    uvicorn.run("hakham.web_v11:app", host="127.0.0.1", port=8765, reload=False)


if __name__ == "__main__":
    main()
