"""研究项目领域实体。"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import uuid4


class ProjectStatus(StrEnum):
    """项目状态。"""

    DRAFT = "draft"  # 草稿
    LITERATURE_REVIEW = "literature_review"  # 文献综述中
    WRITING = "writing"  # 撰写中
    REVISING = "revising"  # 修改中
    COMPLETED = "completed"  # 已完成


@dataclass
class Project:
    """研究项目领域实体。"""

    title: str
    description: str = ""
    id: str = field(default_factory=lambda: uuid4().hex[:12])
    research_question: str = ""
    hypothesis: str = ""
    methodology: str = ""
    keywords: list[str] = field(default_factory=list)
    status: ProjectStatus = ProjectStatus.DRAFT
    paper_ids: list[str] = field(default_factory=list)
    outline: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def add_paper(self, paper_id: str) -> None:
        """关联论文。"""
        if paper_id not in self.paper_ids:
            self.paper_ids.append(paper_id)
            self.updated_at = datetime.now()

    def set_outline(self, sections: list[str]) -> None:
        """设置论文大纲。"""
        self.outline = sections
        self.updated_at = datetime.now()
