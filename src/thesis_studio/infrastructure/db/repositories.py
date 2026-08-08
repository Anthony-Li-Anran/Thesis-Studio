"""SQLite repository implementations. Implements PaperRepository and ProjectRepository interfaces."""

import json
from collections.abc import Callable
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.models.paper import Paper, PaperStatus
from ...domain.models.project import Project, ProjectStatus
from ...domain.models.settings import AIConfig, ExternalAPIConfig, UserSettings
from .sqlite import PaperModel, ProjectModel, UserSettingsModel, get_session_factory

SessionFactory = Callable[[], AsyncSession]


class SQLitePaperRepository:
    """SQLite-based paper repository implementation."""

    def __init__(
        self,
        session_factory: SessionFactory | None = None,
        user_id: str = "",
    ) -> None:
        self._session_factory: SessionFactory = session_factory or get_session_factory()  # type: ignore[assignment]
        self._user_id = user_id

    async def _get_session(self) -> AsyncSession:
        return self._session_factory()

    async def add(self, paper: Paper) -> str:
        """Add a paper."""
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
        """Get paper by ID."""
        session = await self._get_session()
        async with session:
            result = await session.execute(select(PaperModel).where(PaperModel.id == int(paper_id)))
            model = result.scalar_one_or_none()
            return self._to_domain(model) if model else None

    async def search_by_keywords(self, keywords: list[str], limit: int = 20) -> list[Paper]:
        """Search by keywords."""
        session = await self._get_session()
        async with session:
            stmt = select(PaperModel)
            for kw in keywords:
                stmt = stmt.where(PaperModel.title.contains(kw))
            stmt = stmt.limit(limit)
            result = await session.execute(stmt)
            return [self._to_domain(m) for m in result.scalars().all()]

    async def list_all(self, limit: int = 50, offset: int = 0) -> list[Paper]:
        """List all papers with pagination."""
        session = await self._get_session()
        async with session:
            stmt = select(PaperModel).offset(offset).limit(limit)
            result = await session.execute(stmt)
            return [self._to_domain(m) for m in result.scalars().all()]

    async def update(self, paper: Paper) -> None:
        """Update paper (by id)."""
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
        """Delete paper."""
        session = await self._get_session()
        async with session:
            result = await session.execute(select(PaperModel).where(PaperModel.id == int(paper_id)))
            model = result.scalar_one_or_none()
            if model:
                await session.delete(model)
                await session.commit()

    @staticmethod
    def _to_domain(model: PaperModel) -> Paper:
        """ORM model to domain entity."""
        return Paper(
            id=str(model.id),
            title=str(model.title),
            authors=json.loads(str(model.authors)) if model.authors else [],
            abstract=str(model.abstract or ""),
            year=int(model.year) if model.year is not None else None,
            doi=str(model.doi or ""),
            arxiv_id=str(model.arxiv_id or ""),
            url=str(model.url or ""),
            source=str(model.source or ""),
            keywords=json.loads(str(model.keywords)) if model.keywords else [],
            citation_count=int(model.citation_count) if model.citation_count is not None else 0,
            status=PaperStatus(str(model.status)),
            local_path=str(model.local_path or ""),
            notes=str(model.notes or ""),
        )


class SQLiteProjectRepository:
    """SQLite-based project repository implementation."""

    def __init__(
        self,
        session_factory: SessionFactory | None = None,
        user_id: str = "",
    ) -> None:
        self._session_factory: SessionFactory = session_factory or get_session_factory()  # type: ignore[assignment]
        self._user_id = user_id

    async def _get_session(self) -> AsyncSession:
        return self._session_factory()

    async def add(self, project: Project) -> str:
        """Add a project."""
        session = await self._get_session()
        async with session:
            model = ProjectModel(
                id=project.id,
                user_id=project.user_id or self._user_id,
                title=project.title,
                description=project.description,
                research_question=project.research_question,
                hypothesis=project.hypothesis,
                methodology=project.methodology,
                keywords=json.dumps(project.keywords, ensure_ascii=False),
                status=project.status.value,
                paper_ids=json.dumps(project.paper_ids, ensure_ascii=False),
                outline=json.dumps(project.outline, ensure_ascii=False),
                created_at=project.created_at.isoformat(),
                updated_at=project.updated_at.isoformat(),
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return str(model.id)

    async def get(self, project_id: str, user_id: str = "") -> Project | None:
        """Get project by ID."""
        session = await self._get_session()
        async with session:
            result = await session.execute(
                select(ProjectModel).where(ProjectModel.id == project_id)
            )
            model = result.scalar_one_or_none()
            return self._to_domain(model) if model else None

    async def list_all(self, user_id: str = "") -> list[Project]:
        """List all projects for the user."""
        session = await self._get_session()
        async with session:
            result = await session.execute(
                select(ProjectModel).where(ProjectModel.user_id == (user_id or self._user_id))
            )
            return [self._to_domain(m) for m in result.scalars().all()]

    async def update(self, project: Project) -> None:
        """Update project."""
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
                model.keywords = json.dumps(project.keywords, ensure_ascii=False)  # type: ignore[assignment]
                model.status = project.status.value  # type: ignore[assignment]
                model.paper_ids = json.dumps(project.paper_ids, ensure_ascii=False)  # type: ignore[assignment]
                model.outline = json.dumps(project.outline, ensure_ascii=False)  # type: ignore[assignment]
                model.updated_at = datetime.now().isoformat()  # type: ignore[assignment]
                await session.commit()

    async def delete(self, project_id: str) -> None:
        """Delete project."""
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
        """ORM model to domain entity."""
        return Project(
            id=str(model.id),
            user_id=str(model.user_id or ""),
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



class SQLiteSettingsRepository:
    """用户设置仓库实现。存储为单个 JSON 列。"""

    def __init__(
        self,
        session_factory: SessionFactory | None = None,
        user_id: str = "",
    ) -> None:
        self._session_factory: SessionFactory = session_factory or get_session_factory()  # type: ignore[assignment]
        self._user_id = user_id

    async def _get_session(self) -> AsyncSession:
        return self._session_factory()

    async def get(self, user_id: str = "") -> UserSettings:
        """获取用户设置，不存在则返回空设置。"""
        uid = user_id or self._user_id
        session = await self._get_session()
        async with session:
            result = await session.execute(
                select(UserSettingsModel).where(UserSettingsModel.user_id == uid)
            )
            model = result.scalar_one_or_none()
            if model and model.settings_json:
                return self._from_json(uid, str(model.settings_json))
            return UserSettings(user_id=uid)

    async def save(self, settings: UserSettings) -> None:
        """保存用户设置（upsert）。"""
        session = await self._get_session()
        async with session:
            result = await session.execute(
                select(UserSettingsModel).where(
                    UserSettingsModel.user_id == settings.user_id
                )
            )
            model = result.scalar_one_or_none()
            if model:
                model.settings_json = self._to_json(settings)  # type: ignore[assignment]
            else:
                model = UserSettingsModel(
                    user_id=settings.user_id,
                    settings_json=self._to_json(settings),
                )
                session.add(model)
            await session.commit()

    @staticmethod
    def _to_json(settings: UserSettings) -> str:
        return json.dumps(
            {
                "configs": [
                    {
                        "id": c.id,
                        "name": c.name,
                        "api_endpoint": c.api_endpoint,
                        "api_key": c.api_key,
                        "model": c.model,
                        "agents": c.agents,
                    }
                    for c in settings.configs
                ],
                "external_apis": [
                    {
                        "id": a.id,
                        "service_type": a.service_type,
                        "name": a.name,
                        "endpoint": a.endpoint,
                        "test_url": a.test_url,
                        "needs_key": a.needs_key,
                        "api_key": a.api_key,
                        "enabled": a.enabled,
                    }
                    for a in settings.external_apis
                ],
            },
            ensure_ascii=False,
        )

    @staticmethod
    def _from_json(user_id: str, raw: str) -> UserSettings:
        data = json.loads(raw)
        configs = [
            AIConfig(
                id=c["id"],
                name=c["name"],
                api_endpoint=c["api_endpoint"],
                api_key=c["api_key"],
                model=c["model"],
                agents=c["agents"],
            )
            for c in data.get("configs", [])
        ]
        external_apis = [
            ExternalAPIConfig(
                id=a.get("id", ""),
                service_type=a.get("service_type", ""),
                name=a.get("name", ""),
                endpoint=a.get("endpoint", ""),
                test_url=a.get("test_url", ""),
                needs_key=a.get("needs_key", False),
                api_key=a.get("api_key", ""),
                enabled=a.get("enabled", True),
            )
            for a in data.get("external_apis", [])
        ]
        return UserSettings(user_id=user_id, configs=configs, external_apis=external_apis)


class GuestProjectRepository:
    def __init__(self):
        self._store = {}

    async def add(self, project):
        self._store[project.id] = project
        return project.id

    async def get(self, project_id, user_id=""):
        return self._store.get(project_id)

    async def list_all(self, user_id=""):
        return list(self._store.values())

    async def update(self, project):
        if project.id in self._store:
            self._store[project.id] = project

    async def delete(self, project_id):
        self._store.pop(project_id, None)

    def clear(self):
        self._store.clear()


class GuestSettingsRepository:
    """In-memory settings repository for guest users. Lost on logout."""

    def __init__(self):
        self._store = {}

    async def get(self, user_id: str = "") -> "UserSettings":
        return self._store.get(user_id, UserSettings(user_id=user_id))

    async def save(self, settings: "UserSettings") -> None:
        self._store[settings.user_id] = settings

    def clear(self):
        self._store.clear()
