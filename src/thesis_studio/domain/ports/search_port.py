"""文献检索端口接口。"""

from typing import Protocol

from ..models.search import SearchQuery, SearchResult


class LiteratureSearchProvider(Protocol):
    """文献检索接口。支持多数据源（Semantic Scholar、arXiv 等）。"""

    async def search(self, query: SearchQuery) -> SearchResult:
        """执行文献检索。"""
        ...

    @property
    def source_name(self) -> str:
        """数据源名称。"""
        ...
