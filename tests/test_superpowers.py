from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from hakham.superpowers import canonical_url, install, merge_results, research
from hakham.web_research import WebHit


def test_safe_result_urls():
    assert canonical_url('javascript:alert(1)') == ''
    assert canonical_url('https://user:pass@example.com') == ''
    assert canonical_url('https://EXAMPLE.com/Path#anchor') == 'https://example.com/Path'
    assert canonical_url('https://example.com/path') != canonical_url('https://example.com/Path')


def test_fusion_and_deduplication():
    a = {'url': 'https://example.com/A', 'title': 'A'}
    b = {'url': 'https://example.com/B', 'title': 'B'}
    rows = merge_results([[b, a, a], [a]], 10)
    assert len(rows) == 2
    assert rows[0]['title'] == 'A'
    assert merge_results([[a, b]], 1) == [dict(a, snippet='', score=1 / 61)]


def test_parallel_research_uses_only_public_adapter():
    with patch('hakham.superpowers.WebResearchService._search_duckduckgo', return_value=[WebHit('Example', 'https://example.com')]) as search:
        with patch('hakham.superpowers.WebResearchService._fetch_public_text', side_effect=AssertionError('must not fetch pages')):
            result = research('test query', 'sources', 8)
    assert search.call_count == 3
    assert len(result['items']) == 1
    assert result['provider'] == 'duckduckgo'


@pytest.fixture
def client():
    app = FastAPI()
    install(app)
    return TestClient(app)


def test_panel(client):
    response = client.get('/superpowers')
    assert response.status_code == 200
    assert 'getByteTimeDomainData' in response.text
    assert 'Pesquisa ampliada' in response.text


@pytest.mark.parametrize('params', [{'q': 'x'}, {'q': '  '}, {'q': 'valid', 'limit': 99}, {'q': 'valid', 'focus': 'invalid'}])
def test_validation(client, params):
    assert client.get('/api/superpowers/search', params=params).status_code == 422


def test_provider_failure_is_sanitized(client):
    with patch('hakham.superpowers.research', side_effect=RuntimeError('secret')):
        response = client.get('/api/superpowers/search', params={'q': 'test'})
    assert response.status_code == 502
    assert 'secret' not in response.text


def test_capacity_released_after_failure(client):
    with patch('hakham.superpowers.research', side_effect=RuntimeError()):
        for _ in range(4):
            assert client.get('/api/superpowers/search', params={'q': 'test'}).status_code == 502
