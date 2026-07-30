"""API 路由定义。"""

from fastapi import APIRouter

from ...domain.models.search import SearchQuery
from .dependencies import get_services

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    """健康检查。"""
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# 文献管理
# ---------------------------------------------------------------------------


@router.get("/papers")
async def list_papers(limit: int = 50, offset: int = 0) -> list[dict[str, object]]:
    """列出所有论文。"""
    services = get_services()
    papers = await services.literature_manage.list_papers(limit=limit, offset=offset)
    return [
        {
            "title": p.title,
            "authors": p.authors,
            "year": p.year,
            "abstract": p.abstract[:200],
            "status": p.status.value,
            "source": p.source,
        }
        for p in papers
    ]


@router.get("/papers/{paper_id}")
async def get_paper(paper_id: str) -> dict[str, object] | None:
    """获取单篇论文详情。"""
    services = get_services()
    paper = await services.literature_manage.get_paper(paper_id)
    if paper is None:
        return None
    return {
        "title": paper.title,
        "authors": paper.authors,
        "abstract": paper.abstract,
        "year": paper.year,
        "doi": paper.doi,
        "url": paper.url,
        "source": paper.source,
        "keywords": paper.keywords,
        "citation_count": paper.citation_count,
        "status": paper.status.value,
        "citation": paper.citation,
    }


@router.post("/papers/search")
async def search_papers(query: SearchQuery) -> dict[str, object]:
    """检索文献。"""
    services = get_services()
    result = await services.literature_search.search(query)
    return {
        "total_count": result.total_count,
        "source": result.source,
        "items": result.items,
    }


@router.post("/papers/summary")
async def generate_summary(paper_ids: list[str]) -> dict[str, str]:
    """生成文献综述摘要。"""
    services = get_services()
    summary = await services.literature_manage.generate_summary(paper_ids)
    return {"summary": summary}


# ---------------------------------------------------------------------------
# 论文撰写
# ---------------------------------------------------------------------------


@router.post("/writing/outline")
async def generate_outline(project_id: str) -> dict[str, object]:
    """生成论文大纲。"""
    services = get_services()
    sections = await services.outline.generate_outline(project_id)
    return {"project_id": project_id, "outline": sections}


@router.post("/writing/section")
async def write_section(project_id: str, section_title: str, context: str = "") -> dict[str, str]:
    """撰写论文章节。"""
    services = get_services()
    content = await services.section_writer.write_section(
        project_id=project_id,
        section_title=section_title,
        context=context,
    )
    return {"content": content}


@router.post("/writing/polish")
async def polish_text(text: str) -> dict[str, str]:
    """润色文本。"""
    services = get_services()
    polished = await services.text_polisher.polish_text(text)
    return {"polished": polished}


# ---------------------------------------------------------------------------
# 数据分析
# ---------------------------------------------------------------------------


@router.post("/analysis/describe")
async def analyze_data(data_summary: str) -> dict[str, str]:
    """分析数据描述。"""
    services = get_services()
    result = await services.analysis.analyze_data_description(data_summary)
    return {"analysis": result}
