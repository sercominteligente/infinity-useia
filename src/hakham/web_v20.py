from __future__ import annotations

from fastapi import HTTPException

from . import web as backend
from . import web_v19_8 as previous


app = previous.app


# Preserve the old methods so non-OmniRoute deployments keep their behavior.
_ORIGINAL_SET_MODE = backend.RuntimeState.set_mode
_ORIGINAL_SUMMARY = backend.RuntimeState.summary
_ORIGINAL_MODE_FOR_MODEL = backend.RuntimeState._mode_for_model


def _v20_mode_for_model(model: str) -> str:
    value = (model or "").strip().casefold()
    if value == "gpt-6-astra":
        return "astra"
    if value == "route-llm":
        return "auto"
    if value == "auto" or value.startswith("auto/"):
        return "auto"
    return _ORIGINAL_MODE_FOR_MODEL(model)


def _v20_set_mode(self: backend.RuntimeState, mode: str) -> dict[str, object]:
    mode = mode.strip().casefold()
    state = self.state()

    # AUTO uses OmniRoute only when OmniRoute is the configured everyday provider.
    # Legacy Abacus deployments keep their original AUTO => route-llm behavior.
    if mode == "auto" and state.settings.model_provider == "omniroute" and state.omniroute is not None:
        state.omniroute.model = state.settings.omniroute_model or "auto"
        state.core.provider = "omniroute"
        state.core.model = state.omniroute.model
        self._mode = "auto"
        return self.summary()

    # Premium fuel stays opt-in. The Abacus sidecar is registered only when its
    # local secret exists, so this never silently creates a paid fallback.
    if mode == "astra" and state.settings.model_provider == "omniroute":
        if state.abacus is None:
            raise ValueError("Astra requer ABACUS_ROUTELLM_API_KEY configurada")
        state.abacus.model = "gpt-6-astra"
        state.core.provider = "abacus"
        state.core.model = "gpt-6-astra"
        self._mode = "astra"
        return self.summary()

    if mode == "council" and state.settings.model_provider == "omniroute":
        if state.abacus is None:
            raise ValueError("Conselho requer ABACUS_ROUTELLM_API_KEY configurada")
        if len(state.settings.abacus_council_models) < 2:
            raise ValueError("configure pelo menos dois modelos em HAKHAM_COUNCIL_MODELS antes de ativar o Conselho")
        self._mode = "council"
        return self.summary()

    return _ORIGINAL_SET_MODE(self, mode)


def _v20_summary(self: backend.RuntimeState) -> dict[str, object]:
    data = _ORIGINAL_SUMMARY(self)
    state = self._runtime
    if state is None:
        settings = backend.load_settings()
        data.update(
            {
                "omniroute_configured": bool(settings.omniroute_base_url),
                "omniroute_model": settings.omniroute_model,
                "omniroute_base_url": settings.omniroute_base_url,
            }
        )
        return data

    data["provider"] = state.core.provider
    data["model"] = state.core.model
    data["omniroute_configured"] = state.omniroute is not None
    data["omniroute_model"] = state.omniroute.model if state.omniroute is not None else ""
    data["omniroute_base_url"] = state.omniroute.base_url if state.omniroute is not None else ""
    data["premium_abacus_ready"] = state.abacus is not None
    if state.omniroute is not None:
        data["omniroute_telemetry"] = state.omniroute.telemetry()
    return data


backend.RuntimeState._mode_for_model = staticmethod(_v20_mode_for_model)
backend.RuntimeState.set_mode = _v20_set_mode
backend.RuntimeState.summary = _v20_summary


@app.get("/api/omniroute/status")
def omniroute_status() -> dict[str, object]:
    state = backend.runtime.state()
    if state.omniroute is None:
        raise HTTPException(status_code=503, detail="OmniRoute não está configurado")
    try:
        health = state.omniroute.health()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"OmniRoute indisponível: {type(exc).__name__}: {exc}") from exc
    health["telemetry"] = state.omniroute.telemetry()
    health["active"] = state.core.provider == "omniroute"
    return health


OMNIROUTE_UI = r"""
<style id="hakham-v20-omniroute">
.omniroute-chip{display:inline-flex;align-items:center;gap:6px;min-height:30px;padding:0 9px;border:1px solid rgba(86,229,161,.28);border-radius:999px;background:rgba(4,31,27,.72);color:#83b9a8;font-size:9px;font-weight:900;letter-spacing:.07em;white-space:nowrap}.omniroute-chip:before{content:"";width:6px;height:6px;border-radius:50%;background:#8095a0;box-shadow:0 0 9px rgba(128,149,160,.6)}.omniroute-chip.ready{color:#9affd6;border-color:rgba(39,224,173,.42)}.omniroute-chip.ready:before{background:#27e0ad;box-shadow:0 0 12px #27e0ad}.omniroute-chip.error{color:#ffb3c1;border-color:rgba(255,100,123,.35)}.omniroute-chip.error:before{background:#ff647b;box-shadow:0 0 10px #ff647b}
@media(max-width:900px){.omniroute-chip{display:none}}
</style>
"""

OMNIROUTE_SCRIPT = r"""
<script id="hakham-v20-omniroute-js">
(function(){
  function chip(){let el=document.querySelector('#omnirouteChip');if(el)return el;el=document.createElement('span');el.id='omnirouteChip';el.className='omniroute-chip';el.textContent='OMNIROUTE · VERIFICANDO';const right=document.querySelector('.topright'),voice=document.querySelector('#hakhamVoiceHealth');if(right){if(voice&&voice.parentElement===right)voice.insertAdjacentElement('afterend',el);else right.appendChild(el)}return el}
  async function refresh(){const el=chip();try{const r=await fetch('/api/omniroute/status',{cache:'no-store'});let d={};try{d=await r.json()}catch(e){};if(!r.ok)throw new Error(d.detail||('HTTP '+r.status));el.classList.add('ready');el.classList.remove('error');el.textContent='OMNIROUTE · '+String(d.configured_model||'AUTO').toUpperCase()+(d.active?' · ATIVO':'')}catch(e){el.classList.remove('ready');el.classList.add('error');el.textContent='OMNIROUTE · OFFLINE'}}
  refresh();setInterval(refresh,90000);
})();
</script>
"""


def _enhance(html: str) -> str:
    html = html.replace("Orbit Command v0.19.8 Field Vision Phase 1", "Orbit Command v0.20 OmniRoute Economy")
    html = html.replace("ORBIT COMMAND // v0.19.8 FIELD VISION PHASE 1", "ORBIT COMMAND // v0.20 OMNIROUTE ECONOMY")
    html = html.replace("HAKHAM INFINITY ∞ v0.19.8 // SER Comtec", "HAKHAM INFINITY ∞ v0.20 // SER Comtec")
    html = html.replace("</head>", OMNIROUTE_UI + "\n</head>")
    html = html.replace("</body>", OMNIROUTE_SCRIPT + "\n</body>")
    return html


_stable_web = previous._stable_web
_stable_web.CONTROL_CENTER_HTML = _enhance(_stable_web.CONTROL_CENTER_HTML)
CONTROL_CENTER_HTML = _stable_web.CONTROL_CENTER_HTML


def main() -> None:
    import uvicorn

    uvicorn.run("hakham.web_v20:app", host="127.0.0.1", port=8765, reload=False)


if __name__ == "__main__":
    main()
