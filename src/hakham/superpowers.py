"""Read-only research cockpit; no arbitrary URL fetching or paid fallback."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from threading import BoundedSemaphore
from urllib.parse import urlsplit, urlunsplit

from fastapi import HTTPException, Query
from fastapi.responses import HTMLResponse

from .web_research import WebResearchService

_CAPACITY = BoundedSemaphore(2)


def canonical_url(value: str) -> str:
    try:
        parsed = urlsplit(value.strip())
        if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
            return ""
        return urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path or "/", parsed.query, ""))
    except ValueError:
        return ""


def merge_results(batches: list[list[dict]], limit: int) -> list[dict]:
    """Reciprocal rank fusion across query variants, preserving distinct URL paths."""
    merged: dict[str, dict] = {}
    for batch in batches:
        seen: set[str] = set()
        for rank, item in enumerate(batch, 1):
            url = canonical_url(str(item.get("url", "")))
            if not url or url in seen:
                continue
            seen.add(url)
            if url not in merged:
                merged[url] = {"title": str(item.get("title") or url)[:500], "url": url,
                               "snippet": str(item.get("snippet", ""))[:1600], "score": 0.0}
            merged[url]["score"] += 1 / (60 + rank)
    return sorted(merged.values(), key=lambda row: row["score"], reverse=True)[:limit]


def research(query: str, focus: str, limit: int) -> dict:
    variants = [query]
    if focus == "compare":
        variants += [f"{query} vantagens limitações", f"{query} alternativas comparação"]
    elif focus == "sources":
        variants += [f"{query} documentação oficial", f"{query} estudo pesquisa"]

    def search_one(text: str) -> list[dict]:
        # Separate instance per worker; never mutate shared provider state.
        service = WebResearchService(timeout=12.0)
        service.max_results = limit
        # Deliberately reuse only the existing public-search adapter. No page
        # enrichment, arbitrary target fetch, API key or billable fallback here.
        return [hit.as_dict() for hit in service._search_duckduckgo([text])]

    with ThreadPoolExecutor(max_workers=3) as pool:
        batches = list(pool.map(search_one, variants))
    items = merge_results(batches, limit)
    return {"query": query, "queries": variants, "provider": "duckduckgo",
            "retrieved_at": datetime.now(timezone.utc).isoformat(), "items": items,
            "notice": "Trechos externos não verificados; abra as fontes para conferir."
            if items else "Sem resultados. O provedor pode estar indisponível ou bloquear consultas; tente novamente mais tarde."}


def install(app) -> None:
    @app.get("/superpowers", response_class=HTMLResponse, include_in_schema=False)
    def cockpit():
        return HTMLResponse(Path(__file__).with_name("assets").joinpath("superpowers.html").read_text(encoding="utf-8"),
                            headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"})

    @app.get("/api/superpowers/search")
    def search(q: str = Query(min_length=2, max_length=350),
               focus: str = Query(default="sources", pattern="^(simple|sources|compare)$"),
               limit: int = Query(default=8, ge=1, le=12)):
        q = q.strip()
        if len(q) < 2:
            raise HTTPException(422, "Informe pelo menos dois caracteres.")
        if not _CAPACITY.acquire(blocking=False):
            raise HTTPException(429, "Pesquisa ocupada. Aguarde e tente novamente.")
        try:
            return research(q, focus, limit)
        except Exception:
            raise HTTPException(502, "Pesquisa temporariamente indisponível.") from None
        finally:
            _CAPACITY.release()
