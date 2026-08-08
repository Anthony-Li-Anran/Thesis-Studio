"""Semantic Scholar API client."""

import asyncio
from typing import Any

import httpx

from ...config.settings import get_settings
from ...domain.exceptions import LiteratureError
from ...domain.skill.interfaces import SearchQuery
from ..logging import get_logger

logger = get_logger(__name__)

BASE_URL = "https://api.semanticscholar.org/graph/v1"
SEARCH_FIELDS = "title,abstract,authors,year,url,externalIds,citationCount,venue"


class SemanticScholarClient:
    """Async client for Semantic Scholar Academic Graph API."""

    def __init__(self, api_key: str | None = None) -> None:
        settings = get_settings()
        self._api_key = api_key or settings.semantic_scholar_api_key
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            headers: dict[str, str] = {}
            if self._api_key:
                headers["x-api-key"] = self._api_key
            self._client = httpx.AsyncClient(
                base_url=BASE_URL,
                headers=headers,
                timeout=30.0,
            )
        return self._client

    async def search(self, query: SearchQuery) -> list[dict[str, Any]]:
        """Search papers by keyword."""
        client = await self._get_client()
        params: dict[str, Any] = {
            "query": query.keywords,
            "limit": min(query.max_results, 100),
            "fields": SEARCH_FIELDS,
        }
        if query.year_from:
            params["year"] = f"{query.year_from}-{query.year_to or ''}"
        max_retries = 3
        for attempt in range(max_retries + 1):
            try:
                resp = await client.get("/paper/search", params=params)
                resp.raise_for_status()
                data = resp.json()
                return data.get("data", [])
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429 and attempt < max_retries:
                    wait = (attempt + 1) * 5
                    logger.warning(
                        "Semantic Scholar 429, retrying in %ds...", wait
                    )
                    await asyncio.sleep(wait)
                    continue
                logger.error("Semantic Scholar API error: %s", e)
                raise LiteratureError(
                    f"Semantic Scholar search failed: {e.response.status_code}"
                ) from e
            except httpx.RequestError as e:
                logger.error("Semantic Scholar request error: %s", e)
                raise LiteratureError(
                    "Semantic Scholar connection failed"
                ) from e
        return []

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
