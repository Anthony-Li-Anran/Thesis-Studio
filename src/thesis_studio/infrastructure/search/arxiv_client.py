"""arXiv API client using the official arxiv Python package."""

import asyncio
from typing import Any

import arxiv

from ...domain.exceptions import LiteratureError
from ...domain.skill.interfaces import SearchQuery
from ..logging import get_logger

logger = get_logger(__name__)


class ArxivClient:
    """Async client for arXiv API using the official arxiv package.

    The arxiv package handles rate limiting, retries, and pagination
    internally (3s delay between requests, max 1000 results).
    """

    def __init__(self) -> None:
        self._client = arxiv.Client()

    async def search(self, query: SearchQuery) -> list[dict[str, Any]]:
        """Search arXiv by keyword."""
        arxiv_query = arxiv.Search(
            query=query.keywords,
            max_results=min(query.max_results, 15),
            sort_by=arxiv.SortCriterion.Relevance,
        )
        try:
            results = await asyncio.wait_for(
                asyncio.to_thread(list, self._client.results(arxiv_query)),
                timeout=60.0,
            )
        except TimeoutError:
            logger.error("arXiv search timed out after 60s")
            raise LiteratureError("arXiv search timed out")
        except Exception as e:
            logger.error("arXiv search error: %s", e)
            raise LiteratureError(
                f"arXiv search failed: {e}"
            ) from e

        papers: list[dict[str, Any]] = []
        for r in results:
            arxiv_id = r.entry_id.split("/")[-1]
            papers.append({
                "paperId": f"arxiv:{arxiv_id}",
                "title": r.title or "",
                "abstract": r.summary or "",
                "authors": [
                    {"name": a.name} for a in r.authors
                ],
                "year": r.published.year if r.published else None,
                "url": r.entry_id or "",
                "source": "arxiv",
            })
        return papers

    async def close(self) -> None:
        pass  # arxiv.Client uses sessions internally, no manual close needed
