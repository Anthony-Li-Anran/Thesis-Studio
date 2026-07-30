"""SQLite 仓储实现。实现 PaperRepository 和 ProjectRepository 端口。"""

import json
from collections.abc import Callable
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.models.paper import Paper, PaperStatus
from ...domain.models.project import Project, ProjectStatus
from .sqlite import PaperModel, ProjectModel, get_session_factory

SessionFactory = Callable[[], AsyncSession]


class SQLitePaperRepository:
    """基于 SQLite 的论文仓储实现。"""

    def __init__(
        self,
        session_factory: SessionFactory | None = None,
    ) -> None:
        self._session_factory: SessionFactory = session_factory or get_session_factory  # type: ignore[assignment]

    async def _get_session(self) -> AsyncSession:
        return self._session_factory()

    async def add(self, paper: Paper) -> str:
        """添加论文。"""
        session = await self._get_session()
        async with session:
            model = PaperModel(
                title=paper.title,
                authors=json.dumps(paper.authors, ensure_ascii=False),
                abstract=paper.abstract,
                year=paper.year,
                doi=paper.doi,
                arxiv_id=paper.arxiv_id,
                url=paper.url,
                source=paper.source,
                keywords=json.dumps(paper.keywords, ensure_ascii=False),
                citation_count=paper.citation_count,
                status=paper.status.value,
                local_path=paper.local_path,
                notes=paper.notes,
                created_at=paper.created_at.isoformat(),
                updated_at=paper.updated_at.isoformat(),
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return str(model.id)

    async def get(self, paper_id: str) -> Paper | None:
        """按 ID 获取论文。"""
        session = await self._get_session()
        async with session:
            result = await session.execute(select(PaperModel).where(PaperModel.id == int(paper_id)))
            model = result.scalar_one_or_none()
            return self._to_domain(model) if model else None

    async def search_by_keywords(self, keywords: list[str], limit: int = 20) -> list[Paper]:
        """按关键词搜索。"""
        session = await self._get_session()
        async with session:
            stmt = select(PaperModel)
            for kw in keywords:
                stmt = stmt.where(PaperModel.title.contains(kw))
            stmt = stmt.limit(limit)
            result = await session.execute(stmt)
            return [self._to_domain(m) for m in result.scalars().all()]

    async def list_all(self, limit: int = 50, offset: int = 0) -> list[Paper]:
        """分页列出所有论文。"""
        session = await self._get_session()
        async with session:
            stmt = select(PaperModel).offset(offset).limit(limit)
            result = await session.execute(stmt)
            return [self._to_domain(m) for m in result.scalars().all()]

    async def update(self, paper: Paper) -> None:
        """更新论文（按 id 定位）。"""
        session = await self._get_session()
        async with session:
            result = await session.execute(select(PaperModel).where(PaperModel.id == int(paper.id)))
            model = result.scalar_one_or_none()
            if model:
                model.title = paper.title  # type: ignore[assignment]
                model.status = paper.status.value  # type: ignore[assignment]
                model.notes = paper.notes  # type: ignore[assignment]
                model.local_path = paper.local_path  # type: ignore[assignment]
                model.updated_at = datetime.now().isoformat()  # type: ignore[assignment]
                await session.commit()

    async def delete(self, paper_id: str) -> None:
        """删除论文。"""
        session = await self._get_session()
        async with session:
            result = await session.execute(select(PaperModel).where(PaperModel.id == int(paper_id)))
            model = result.scalar_one_or_none()
            if model:
                await session.delete(model)
                await session.commit()

    @staticmethod
    def _to_domain(model: PaperModel) -> Paper:
        """ORM 模型 → 领域实体。"""
        return Paper(
            id=str(model.id),
            title=str(model.title),
            authors=json.loads(str(model.authors)) if model.authors else [],
            abstract=str(model.abstract or ""),
            year=int(model.year) if model.year is not None else None,
            doi=str(model.doi) if model.doi else None,
            arxiv_id=str(model.arxiv_id) if model.arxiv_id else None,
            url=str(model.url or ""),
            source=str(model.source or ""),
            keywords=json.loads(str(model.keywords)) if model.keywords else [],
            citation_count=int(model.citation_count or 0),
            status=PaperStatus(str(model.status)),
            local_path=str(model.local_path) if model.local_path else None,
            notes=str(model.notes or ""),
        )


class SQLiteProjectRepository:
    """基于 SQLite 的项目仓储实现。"""

    def __init__(
        self,
        session_factory: SessionFactory | None = None,
    ) -> None:
        self._session_factory: SessionFactory = session_factory or get_session_factory  # type: ignore[assignment]

    async def _get_session(self) -> AsyncSession:
        return self._session_factory()

    async def add(self, project: Project) -> str:
        """创建项目。"""
        session = await self._get_session()
        async with session:
            model = ProjectModel(
                id=project.id,
                title=project.title,
                description=project.description,
                research_question=project.research_question,
                hypothesis=project.hypothesis,
                methodology=project.methodology,
                keywords=json.dumps(project.keywords, ensure_ascii=False),
                status=project.status.value,
                paper_ids=json.dumps(project.paper_ids),
                outline=json.dumps(project.outline, ensure_ascii=False),
                created_at=project.created_at.isoformat(),
                updated_at=project.updated_at.isoformat(),
            )
            session.add(model)
            await session.commit()
            return str(model.id)

    async def get(self, project_id: str) -> Project | None:
        """按 ID 获取项目。"""
        session = await self._get_session()
        async with session:
            result = await session.execute(
                select(ProjectModel).where(ProjectModel.id == project_id)
            )
            model = result.scalar_one_or_none()
            return self._to_domain(model) if model else None

    async def list_all(self) -> list[Project]:
        """列出所有项目。"""
        session = await self._get_session()
        async with session:
            result = await session.execute(select(ProjectModel))
            return [self._to_domain(m) for m in result.scalars().all()]

    async def update(self, project: Project) -> None:
        """更新项目。"""
        session = await self._get_session()
        async with session:
            result = await session.execute(
                select(ProjectModel).where(ProjectModel.id == project.id)
            )
            model = result.scalar_one_or_none()
            if model:
                model.title = project.title  # type: ignore[assignment]
                model.description = project.description  # type: ignore[assignment]
                model.research_question = project.research_question  # type: ignore[assignment]
                model.hypothesis = project.hypothesis  # type: ignore[assignment]
                model.methodology = project.methodology  # type: ignore[assignment]
                model.status = project.status.value  # type: ignore[assignment]
                model.paper_ids = json.dumps(project.paper_ids)  # type: ignore[assignment]
                model.outline = json.dumps(project.outline, ensure_ascii=False)  # type: ignore[assignment]
                model.updated_at = datetime.now().isoformat()  # type: ignore[assignment]
                await session.commit()

    async def delete(self, project_id: str) -> None:
        """删除项目。"""
        session = await self._get_session()
        async with session:
            result = await session.execute(
                select(ProjectModel).where(ProjectModel.id == project_id)
            )
            model = result.scalar_one_or_none()
            if model:
                await session.delete(model)
                await session.commit()

    @staticmethod
    def _to_domain(model: ProjectModel) -> Project:
        """ORM 模型 → 领域实体。"""
        return Project(
            id=str(model.id),
            title=str(model.title),
            description=str(model.description or ""),
            research_question=str(model.research_question or ""),
            hypothesis=str(model.hypothesis or ""),
            methodology=str(model.methodology or ""),
            keywords=json.loads(str(model.keywords)) if model.keywords else [],
            status=ProjectStatus(str(model.status)),
            paper_ids=json.loads(str(model.paper_ids)) if model.paper_ids else [],
            outline=json.loads(str(model.outline)) if model.outline else [],
        )
