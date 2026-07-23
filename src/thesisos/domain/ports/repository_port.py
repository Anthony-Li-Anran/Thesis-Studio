"""仓储端口接口：定义数据持久化的抽象。"""

from typing import Protocol

from ..models.paper import Paper
from ..models.project import Project


class PaperRepository(Protocol):
    """论文仓储接口。"""

    async def add(self, paper: Paper) -> str:
        """添加论文，返回 ID。"""
        ...

    async def get(self, paper_id: str) -> Paper | None:
        """按 ID 获取论文。"""
        ...

    async def search_by_keywords(self, keywords: list[str], limit: int = 20) -> list[Paper]:
        """按关键词搜索论文。"""
        ...

    async def list_all(self, limit: int = 50, offset: int = 0) -> list[Paper]:
        """分页列出所有论文。"""
        ...

    async def update(self, paper: Paper) -> None:
        """更新论文。"""
        ...

    async def delete(self, paper_id: str) -> None:
        """删除论文。"""
        ...


class ProjectRepository(Protocol):
    """项目仓储接口。"""

    async def add(self, project: Project) -> str:
        """创建项目，返回 ID。"""
        ...

    async def get(self, project_id: str) -> Project | None:
        """按 ID 获取项目。"""
        ...

    async def list_all(self) -> list[Project]:
        """列出所有项目。"""
        ...

    async def update(self, project: Project) -> None:
        """更新项目。"""
        ...

    async def delete(self, project_id: str) -> None:
        """删除项目。"""
        ...
