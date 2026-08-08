"""Researcher domain logic — pure functions, no LLM or I/O."""

from dataclasses import dataclass, field


@dataclass
class Paper:
    """A single academic paper."""

    paper_id: str
    title: str
    abstract: str = ""
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    url: str = ""
    source: str = ""
    citation_count: int = 0


@dataclass
class PaperCluster:
    """A cluster of papers grouped by theme (AI-judged)."""

    theme: str
    description: str
    papers: list[Paper] = field(default_factory=list)


@dataclass
class GraphEdge:
    """A relationship edge between two papers in the knowledge graph."""

    source_id: str
    target_id: str
    relation: str  # e.g. "同主题", "矛盾", "继承", "扩展"
    description: str = ""


@dataclass
class LiteratureReview:
    """Structured literature review output from EXPLORING phase."""

    topic: str
    clusters: list[PaperCluster] = field(default_factory=list)
    edges: list[GraphEdge] = field(default_factory=list)
    introduction: str = ""
    methodology: str = ""
    summary: str = ""
    cross_cutting: str = ""
    research_gaps: list[str] = field(default_factory=list)
    key_debates: list[str] = field(default_factory=list)
    future_directions: list[str] = field(default_factory=list)
    conclusion: str = ""
    keywords: list[str] = field(default_factory=list)


def build_review(
    topic: str,
    clusters: list[PaperCluster],
    edges: list[GraphEdge],
    gaps: list[str],
    debates: list[str],
    summary: str,
) -> LiteratureReview:
    """Build a structured literature review."""
    return LiteratureReview(
        topic=topic,
        clusters=clusters,
        edges=edges,
        research_gaps=gaps,
        key_debates=debates,
        summary=summary,
    )
