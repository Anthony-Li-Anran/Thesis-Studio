"""文献检索用例：编排检索流程。"""

from ...domain.models.paper import Paper, PaperStatus
from ...domain.models.search import SearchQuery, SearchResult
from ...domain.ports.repository_port import PaperRepository
from ...domain.ports.search_port import LiteratureSearchProvider


class LiteratureSearchService:
    """文献检索用例。编排多源检索 → 去重 → 入库流程。"""

    def __init__(
        self,
        search_providers: list[LiteratureSearchProvider],
        paper_repo: PaperRepository,
    ) -> None:
        self._providers = search_providers
        self._paper_repo = paper_repo

    async def search(self, query: SearchQuery) -> SearchResult:
        """执行多源文献检索并入库。"""
        all_items: list[dict[str, object]] = []
        total_count = 0

        for provider in self._providers:
            result = await provider.search(query)
            all_items.extend(result.items)
            total_count += result.total_count

        # 去重（按 title 相似度）
        seen: set[str] = set()
        unique_items: list[dict[str, object]] = []
        for item in all_items:
            title = str(item.get("title", "")).lower().strip()
            if title and title not in seen:
                seen.add(title)
                unique_items.append(item)

        return SearchResult(
            query=query,
            total_count=len(unique_items),
            items=unique_items[: query.max_results],
            source="+".join(p.source_name for p in self._providers),
        )

    async def search_and_save(self, query: SearchQuery) -> list[Paper]:
        """检索并保存论文到数据库。"""
        result = await self.search(query)
        papers: list[Paper] = []

        for item in result.items:
            paper = Paper.from_dict(dict(item))
            paper.source = result.source
            paper.keywords = query.keywords.split()
            paper.status = PaperStatus.DISCOVERED
            await self._paper_repo.add(paper)
            papers.append(paper)

        return papers
