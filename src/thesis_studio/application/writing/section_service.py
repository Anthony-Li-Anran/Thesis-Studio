"""章节撰写服务：根据大纲撰写论文各章节内容。"""

from ...domain.exceptions import ValidationError
from ...domain.ports.llm_port import LLMProvider
from ...domain.ports.repository_port import ProjectRepository


class SectionWriter:
    """论文章节撰写服务。"""

    def __init__(
        self,
        llm: LLMProvider,
        project_repo: ProjectRepository,
    ) -> None:
        self._llm = llm
        self._project_repo = project_repo

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

        prompt = f"""你是一位学术写作专家。请撰写以下论文章节：

论文题目：{project.title}
研究问题：{project.research_question}
研究方法：{project.methodology}

章节：{section_title}

{context}

请撰写该章节的完整内容，语言学术化但清晰易懂。用中文撰写，约 800-1500 字。"""

        return await self._llm.generate(prompt, temperature=0.6, max_tokens=3000)
