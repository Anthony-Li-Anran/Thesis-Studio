"""Skill interfaces for EXPLORING phase.

Four skills:
- AcademicSearch: query academic databases
- PaperParser: parse and extract paper metadata
- Cluster: AI-judged paper clustering by theme
- ReviewGen: generate structured literature review
"""

from typing import Any

from pydantic import BaseModel, Field, field_validator

from ..agent.researcher import LiteratureReview, Paper, PaperCluster


class SearchQuery(BaseModel):
    """A search query for academic databases."""

    keywords: str
    max_results: int = 20
    year_from: int | None = None
    year_to: int | None = None

    @field_validator("keywords")
    @classmethod
    def keywords_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("搜索关键词不能为空")
        return v.strip()


class AcademicSearchInput(BaseModel):
    """Input for academic search skill."""

    queries: list[SearchQuery] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=lambda: ["semantic_scholar", "arxiv"])


class AcademicSearchOutput(BaseModel):
    """Output from academic search skill."""

    papers: list[dict[str, Any]] = Field(default_factory=list)
    total_count: int = 0


class PaperParserInput(BaseModel):
    """Input for paper parsing skill."""

    raw_papers: list[dict[str, Any]] = Field(default_factory=list)


class PaperParserOutput(BaseModel):
    """Output from paper parsing skill."""

    papers: list[Paper] = Field(default_factory=list)
    duplicates_removed: int = 0


class ClusterInput(BaseModel):
    """Input for AI-judged clustering skill."""

    papers: list[Paper] = Field(default_factory=list)
    topic: str = ""


class ClusterOutput(BaseModel):
    """Output from AI clustering skill."""

    clusters: list[PaperCluster] = Field(default_factory=list)


class ReviewGenInput(BaseModel):
    """Input for literature review generation."""

    topic: str
    clusters: list[PaperCluster] = Field(default_factory=list)


class ReviewGenOutput(BaseModel):
    """Output from literature review generation."""

    review: LiteratureReview | None = None
    raw_text: str = ""
    html_content: str = ""
