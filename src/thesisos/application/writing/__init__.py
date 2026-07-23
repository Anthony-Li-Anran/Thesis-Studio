"""论文撰写用例。"""

from ...domain.exceptions import ValidationError
from ...domain.models.project import ProjectStatus
from ...domain.ports.llm_port import LLMProvider
from ...domain.ports.repository_port import PaperRepository, ProjectRepository


class WritingService:
    """论文撰写用例：大纲生成、章节撰写、修改润色。"""

    def __init__(
        self,
        llm: LLMProvider,
        project_repo: ProjectRepository,
        paper_repo: PaperRepository,
    ) -> None:
        self._llm = llm
        self._project_repo = project_repo
        self._paper_repo = paper_repo

    async def generate_outline(self, project_id: str) -> list[str]:
        """基于研究问题和文献生成论文大纲。"""
        project = await self._project_repo.get(project_id)
        if project is None:
            raise ValidationError(f"项目不存在: {project_id}")

        papers = await self._paper_repo.list_all(limit=30)

        papers_context = "\n".join(f"- {p.citation}" for p in papers[:20]) if papers else "暂无文献"

        prompt = f"""你是一位学术导师。请为以下研究项目生成论文大纲。

研究题目：{project.title}
研究问题：{project.research_question or "待定"}
研究方法：{project.methodology or "待定"}

相关文献：
{papers_context}

请生成一个完整的论文大纲（章节结构），每章包含 2-4 个小节。用中文回答，格式如下：

第一章 章节标题
  1.1 小节标题
  1.2 小节标题
..."""

        response = await self._llm.generate(prompt, temperature=0.5)
        sections = [
            line.strip()
            for line in response.split("\n")
            if line.strip() and not line.strip().startswith("第")
        ]
        if not sections:
            sections = [line.strip() for line in response.split("\n") if line.strip()]

        project.set_outline(sections)
        project.status = ProjectStatus.WRITING
        await self._project_repo.update(project)

        return sections

    async def write_section(
        self,
        project_id: str,
        section_title: str,
        context: str = "",
    ) -> str:
        """撰写论文章节内容。"""
        project = await self._project_repo.get(project_id)
        if project is None:
            raise ValidationError(f"项目不存在: {project_id}")

        prompt = f"""你是一位学术写作专家。请撰写以下论文章节。

论文题目：{project.title}
研究问题：{project.research_question}
研究方法：{project.methodology}

章节：{section_title}

{context}

请撰写该章节的完整内容，语言学术化但清晰易懂。用中文撰写，约 800-1500 字。"""

        return await self._llm.generate(prompt, temperature=0.6, max_tokens=3000)

    async def polish_text(self, text: str) -> str:
        """润色学术文本。"""
        prompt = f"""你是一位学术写作编辑。请润色以下文本，提升其学术性和可读性，
保持原意不变，修正语法和表达问题：

{text}

请直接返回润色后的文本："""
        return await self._llm.generate(prompt, temperature=0.3)
