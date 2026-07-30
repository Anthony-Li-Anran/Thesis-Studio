"""检索领域值对象。"""

from dataclasses import dataclass, field


@dataclass
class SearchQuery:
    """文献检索查询值对象。"""

    keywords: str
    max_results: int = 20
    year_from: int | None = None
    year_to: int | None = None
    sources: list[str] = field(default_factory=lambda: ["semantic_scholar"])

    def __post_init__(self) -> None:
        if not self.keywords.strip():
            raise ValueError("检索关键词不能为空")
        if self.max_results < 1 or self.max_results > 100:
            raise ValueError("检索结果数需在 1-100 之间")


@dataclass
class SearchResult:
    """文献检索结果值对象。"""

    query: SearchQuery
    total_count: int
    items: list[dict[str, object]] = field(default_factory=list)
    source: str = ""
