from hakham import web_v19_3
from hakham.web_research import WebResearchService


def test_v19_3_context_controls_are_present() -> None:
    html = web_v19_3.CONTROL_CENTER_HTML
    assert web_v19_3.app is not None
    assert "v0.19.3 CONTEXT CONTROLS" in html
    assert "hakham-v19-3-contextual-control-js" in html
    assert "Fechando todos os cards" in html
    assert "dataset.kind===intent.kind" in html
    assert "research:['notícia'" in html
    assert "instagram:['instagram'" in html
    assert "agents:['agente'" in html


def test_v19_3_broadens_current_news_research_intent() -> None:
    assert WebResearchService.should_research("Busque notícias do mercado financeiro no Google") is True
    assert WebResearchService.should_research("Quais as notícias de esportes hoje?") is True
    assert WebResearchService.should_research("Veja as manchetes do dia") is True
