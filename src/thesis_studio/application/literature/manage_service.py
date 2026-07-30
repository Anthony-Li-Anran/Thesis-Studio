"""文献管理用例。"""

from ...domain.exceptions import ValidationError
from ...domain.models.paper import Paper, PaperStatus
from ...domain.ports.llm_port import LLMProvider
from ...domain.ports.repository_port import PaperRepository


class LiteratureManageService:
    """文献管理用例：论文筛选、分类、综述生成。"""

    def __init__(self, paper_repo: PaperRepository, llm: LLMProvider) -> None:
        self._paper_repo = paper_repo
        self._llm = llm

    async def list_papers(self, limit: int = 50, offset: int = 0) -> list[Paper]:
        """列出所有论文。"""
        return await self._paper_repo.list_all(limit=limit, offset=offset)

    async def get_paper(self, paper_id: str) -> Paper | None:
        """获取单篇论文。"""
        return await self._paper_repo.get(paper_id)

    async def update_status(self, paper_id: str, status: PaperStatus) -> None:
        """更新论文状态。"""
        paper = await self._paper_repo.get(paper_id)
        if paper is None:
            raise ValidationError(f"论文不存在: {paper_id}")
        paper.status = status
        await self._paper_repo.update(paper)

    async def generate_summary(self, paper_ids: list[str]) -> str:
        """基于选定论文生成文献综述摘要。"""
        papers = []
        for pid in paper_ids:
            paper = await self._paper_repo.get(pid)
            if paper:
                papers.append(paper)

        if not papers:
            return "未找到相关论文。"

        papers_text = "\n\n".join(
            f"{i + 1}. {p.citation}\n   {p.abstract[:300]}" for i, p in enumerate(papers)
        )

        prompt = f"""你是一位学术研究助手。请基于以下论文，撰写一段简洁的文献综述摘要（300-500字），
概括该领域的研究现状、主要方向和关键发现。

论文列表：
{papers_text}

请用中文撰写文献综述摘要："""

        return await self._llm.generate(prompt, temperature=0.5)
