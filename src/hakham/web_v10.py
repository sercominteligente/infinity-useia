from __future__ import annotations

from . import web_v9 as vision_layer


app = vision_layer.app

WHATSAPP_UI = r"""
<style id="hakham-v10-whatsapp">
.wabar{display:grid;grid-template-columns:minmax(180px,.45fr) minmax(0,1fr) auto;gap:8px;align-items:center;margin:0 0 9px;padding:8px 10px;border:1px solid rgba(39,224,173,.24);border-radius:11px;background:rgba(3,30,29,.42)}
.wabar input{height:40px;border:1px solid rgba(39,224,173,.32);border-radius:9px;background:rgba(1,14,18,.78);color:#efffff;padding:0 11px;outline:none}.wabar .walabel{font-size:12px;color:#91bcb5;white-space:nowrap}.wabar button{height:40px;border:1px solid rgba(39,224,173,.5);border-radius:9px;background:rgba(9,63,54,.78);color:#dffff7;padding:0 14px;font-weight:800;cursor:pointer}.wabar button:hover{border-color:#4ff0c2}.wabar button:disabled{opacity:.45;cursor:not-allowed}.wabar small{grid-column:1/-1;color:#749b97}.wabar .rednote{color:#ff8fa1}.wa-state{display:inline-flex;align-items:center;gap:6px;margin-left:8px;font-size:10px;font-weight:800;letter-spacing:.05em}.wa-state.ok{color:#27e0ad}.wa-state.bad{color:#ff8fa1}.wa-state.wait{color:#f4b75b}
@media(max-width:760px){.wabar{grid-template-columns:1fr}.wabar button,.wabar input{width:100%}.wabar .walabel{white-space:normal}.wa-state{margin-left:0}}
</style>
"""

WHATSAPP_BAR = r"""<div class="wabar"><span class="walabel">📲 WHATSAPP CONTROL <span id="waState" class="wa-state wait">VERIFICANDO</span></span><input id="waNumber" inputmode="tel" placeholder="55 + DDD + número"><button id="waSendBtn" type="button">PREPARAR ENVIO</button><small>Usa o texto que estiver no campo principal do chat. <span class="rednote">O envio só acontece após sua confirmação explícita.</span> <button id="waTestBtn" type="button" style="height:28px;padding:0 9px;margin-left:7px">TESTAR CONEXÃO</button></small></div>"""

WHATSAPP_SCRIPT = r"""
<script id="hakham-v10-whatsapp-js">
(function(){
  const btn=document.querySelector('#waSendBtn'),number=document.querySelector('#waNumber'),stateEl=document.querySelector('#waState'),testBtn=document.querySelector('#waTestBtn');
  if(!btn||!number)return;
  let waConnected=false;
  function bubble(role,text){
    if(typeof addBubble==='function'){addBubble(role,text);return}
    const log=document.querySelector('#chatLog');if(!log)return;const d=document.createElement('div');d.className='bubble';const s=document.createElement('strong');s.textContent=role;d.appendChild(s);d.appendChild(document.createTextNode(text));log.appendChild(d);log.scrollTop=log.scrollHeight;
  }
  function setWaState(text,kind){if(!stateEl)return;stateEl.textContent=text;stateEl.className='wa-state '+(kind||'wait')}
  function extractState(payload){
    const r=payload?.result||payload||{};
    return String(r?.instance?.state||r?.state||r?.instance?.status||r?.status||'').toLowerCase();
  }
  async function checkConnection(showBubble){
    setWaState('VERIFICANDO','wait');
    try{
      const r=await fetch('/api/tools/execute',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({tool_id:'whatsapp.status',arguments:{},approved:false})});
      let d={};try{d=await r.json()}catch(e){}
      if(!r.ok)throw new Error(d.detail||('HTTP '+r.status));
      const state=extractState(d);
      waConnected=['open','connected','online','ready'].includes(state);
      setWaState(waConnected?'CONECTADO':(state?state.toUpperCase():'STATUS DESCONHECIDO'),waConnected?'ok':'bad');
      if(showBubble)bubble('HAKHAM · WHATSAPP',waConnected?'Evolution conectada e pronta para envio.':'Evolution respondeu, mas a instância não está conectada. Estado: '+(state||'desconhecido')+'.');
      return waConnected;
    }catch(e){
      waConnected=false;setWaState('INDISPONÍVEL','bad');
      if(showBubble)bubble('HAKHAM · WHATSAPP','WhatsApp não está pronto: '+e.message+'. Verifique EVOLUTION_API_URL, EVOLUTION_API_KEY e EVOLUTION_INSTANCE no .env e reinicie o Hakham.');
      return false;
    }
  }
  if(testBtn)testBtn.addEventListener('click',()=>checkConnection(true));
  btn.addEventListener('click',async()=>{
    const phone=number.value.replace(/\D/g,'');
    const input=document.querySelector('#chatInput');
    const text=(input?.value||'').trim();
    if(!phone){if(typeof toast==='function')toast('Informe o número com DDI e DDD');number.focus();return}
    if(!text){if(typeof toast==='function')toast('Escreva a mensagem no campo do chat');input?.focus();return}
    if(!(await checkConnection(false))){bubble('HAKHAM · WHATSAPP','Envio bloqueado porque a instância Evolution não está conectada. Toque em TESTAR CONEXÃO para ver o diagnóstico.');return}
    const approved=window.confirm('Autorizar HAKHAM Infinity a enviar esta mensagem pelo WhatsApp para '+phone+'?\n\n'+text);
    if(!approved){if(typeof toast==='function')toast('Envio cancelado pelo Ach');return}
    btn.disabled=true;btn.textContent='ENVIANDO...';if(typeof setState==='function')setState('executing','WHATSAPP');
    try{
      const r=await fetch('/api/tools/execute',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({tool_id:'whatsapp.send_text',arguments:{number:phone,text:text},approved:true})});
      let d={};try{d=await r.json()}catch(e){}
      if(!r.ok)throw new Error(d.detail||('HTTP '+r.status));
      const result=d.result||{};const msgId=result?.key?.id||result?.id||result?.messageId||'';
      bubble('HAKHAM · WHATSAPP','A Evolution aceitou o envio para '+phone+(msgId?' · ID '+msgId:'')+'. A confirmação de entrega depende do estado retornado pelo WhatsApp/Evolution.');
      if(typeof toast==='function')toast('Envio aceito pela Evolution');
      if(input)input.value='';
    }catch(e){bubble('HAKHAM · WHATSAPP','Não consegui enviar a mensagem: '+e.message);if(typeof toast==='function')toast('WhatsApp: '+e.message)}
    finally{btn.disabled=false;btn.textContent='PREPARAR ENVIO';if(typeof setState==='function')setState('idle','EM ESPERA')}
  });
  setTimeout(()=>checkConnection(false),700);
})();
</script>
"""


def _enhance(html: str) -> str:
    html = html.replace("Orbit Command v0.9 Vision", "Orbit Command v0.10 Demo")
    html = html.replace("ORBIT COMMAND // v0.9 VISION", "ORBIT COMMAND // v0.10 DEMO")
    html = html.replace("HAKHAM INFINITY ∞ v0.9 // SER Comtec", "HAKHAM INFINITY ∞ v0.10 // SER Comtec")
    html = html.replace("</head>", WHATSAPP_UI + "\n</head>")
    html = html.replace('<div class="compose">', WHATSAPP_BAR + '<div class="compose">', 1)
    html = html.replace("</body>", WHATSAPP_SCRIPT + "\n</body>")
    return html


vision_layer.previous.CONTROL_CENTER_HTML = _enhance(vision_layer.previous.CONTROL_CENTER_HTML)


def main() -> None:
    import uvicorn

    uvicorn.run("hakham.web_v10:app", host="127.0.0.1", port=8765, reload=False)


if __name__ == "__main__":
    main()
