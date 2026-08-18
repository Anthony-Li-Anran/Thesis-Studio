"""论文领域实体。"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import uuid4


class PaperStatus(StrEnum):
    """论文处理状态。"""

    DISCOVERED = "discovered"  # 新发现
    DOWNLOADED = "downloaded"  # 已下载
    PARSED = "parsed"  # 已解析
    INDEXED = "indexed"  # 已向量化
    REJECTED = "rejected"  # 已排除


@dataclass
class Paper:
    """学术论文领域实体。"""

    title: str
    id: str = field(default_factory=lambda: uuid4().hex[:12])
    authors: list[str] = field(default_factory=list)
    abstract: str = ""
    year: int | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    url: str = ""
    source: str = ""  # semantic_scholar / arxiv / manual
    keywords: list[str] = field(default_factory=list)
    citation_count: int = 0
    status: PaperStatus = PaperStatus.DISCOVERED
    local_path: str | None = None
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    project_id: str = ""

    @property
    def citation(self) -> str:
        """生成简略引用。"""
        authors = ", ".join(self.authors[:3])
        if len(self.authors) > 3:
            authors += " et al."
        year = f" ({self.year})" if self.year else ""
        return f"{authors}.{year} {self.title}."

    @property
    def is_processed(self) -> bool:
        """是否已完成处理。"""
        return self.status == PaperStatus.INDEXED

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Paper":
        """从字典创建 Paper 实体（用于检索结果转换）。"""
        authors_raw = data.get("authors")
        year_raw = data.get("year")
        keywords_raw = data.get("keywords")
        return cls(
            title=str(data.get("title", "")),
            authors=([str(a) for a in authors_raw] if isinstance(authors_raw, list) else []),
            abstract=str(data.get("abstract", "")),
            year=int(year_raw) if isinstance(year_raw, (int, str)) else None,
            doi=str(data.get("doi")) if data.get("doi") else None,
            arxiv_id=str(data.get("arxiv_id")) if data.get("arxiv_id") else None,
            url=str(data.get("url", "")),
            source=str(data.get("source", "")),
            keywords=([str(k) for k in keywords_raw] if isinstance(keywords_raw, list) else []),
        )

    @classmethod
    def from_researcher_dict(cls, data: dict[str, object]) -> "Paper":
        """从 Researcher Agent 产出的字典创建 Paper 实体。"""
        authors_raw = data.get("authors")
        year_raw = data.get("year")
        return cls(
            title=str(data.get("title", "")),
            authors=([str(a) for a in authors_raw] if isinstance(authors_raw, list) else []),
            abstract=str(data.get("abstract", "")),
            year=int(year_raw) if isinstance(year_raw, (int, str)) else None,
            url=str(data.get("url", "")),
            source=str(data.get("source", "")),
            citation_count=int(str(data.get("citation_count", "0"))),
            status=PaperStatus.DISCOVERED,
        )

