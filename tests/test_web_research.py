from hakham.web_research import WebHit, WebResearchService


def test_web_research_detects_explicit_research_intent() -> None:
    assert WebResearchService.should_research("Pesquise na internet a empresa Acme") is True
    assert WebResearchService.should_research("Analise o Instagram da empresa Acme") is True
    assert WebResearchService.should_research("https://example.com") is True
    assert WebResearchService.should_research("Escreva uma legenda curta") is False


def test_company_research_expands_queries() -> None:
    service = WebResearchService()
    queries = service.build_queries("Pesquise a empresa Acme e sua presença digital")
    assert len(queries) >= 3
    assert any("site oficial" in query for query in queries)
    assert any("Instagram Facebook LinkedIn" in query for query in queries)
    assert any("concorrentes" in query for query in queries)


def test_public_url_guard_rejects_local_network_targets() -> None:
    assert WebResearchService._safe_public_url("http://127.0.0.1:8765") is False
    assert WebResearchService._safe_public_url("http://localhost/admin") is False
    assert WebResearchService._safe_public_url("http://192.168.0.10/private") is False
    assert WebResearchService._safe_public_url("https://example.com") is True


def test_dedupe_keeps_first_public_result() -> None:
    hits = [
        WebHit(title="A", url="https://example.com/"),
        WebHit(title="B", url="https://example.com"),
        WebHit(title="C", url="https://example.org"),
    ]
    deduped = WebResearchService._dedupe_hits(hits)
    assert [hit.title for hit in deduped] == ["A", "C"]
