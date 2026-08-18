"""研究项目领域实体。"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import uuid4


class ProjectStatus(StrEnum):
    """项目状态机。"""

    INIT = "init"
    EXPLORING = "exploring"
    DESIGNING = "designing"
    RESEARCHING = "researching"
    WRITING = "writing"
    POLISHING = "polishing"
    COMPLETED = "completed"


STATUS_FLOW: list[ProjectStatus] = [
    ProjectStatus.INIT,
    ProjectStatus.EXPLORING,
    ProjectStatus.DESIGNING,
    ProjectStatus.RESEARCHING,
    ProjectStatus.WRITING,
    ProjectStatus.POLISHING,
    ProjectStatus.COMPLETED,
]


@dataclass
class Project:
    """研究项目领域实体。"""

    title: str
    description: str = ""
    id: str = field(default_factory=lambda: uuid4().hex[:12])
    user_id: str = ""
    research_question: str = ""
    hypothesis: str = ""
    methodology: str = ""
    keywords: list[str] = field(default_factory=list)
    status: ProjectStatus = ProjectStatus.INIT
    paper_ids: list[str] = field(default_factory=list)
    outline: list[str] = field(default_factory=list)
    exploring_state: dict[str, object] = field(default_factory=dict)  # EXPLORING session state
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
