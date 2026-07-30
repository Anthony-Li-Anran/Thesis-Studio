"""SQLite 异步引擎、ORM 模型与会话管理。"""

from collections.abc import AsyncIterator

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from ...config.settings import get_settings
from ..logging import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# ORM 基类与模型（基础设施层内部使用，不暴露到领域层）
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    """所有 ORM 模型的基类。"""


class PaperModel(Base):
    """论文 ORM 模型。"""

    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False, index=True)
    authors = Column(Text, default="")  # JSON 编码的列表
    abstract = Column(Text, default="")
    year = Column(Integer, nullable=True)
    doi = Column(String(200), nullable=True, unique=True)
    arxiv_id = Column(String(100), nullable=True)
    url = Column(String(500), default="")
    source = Column(String(100), default="")
    keywords = Column(Text, default="")
    citation_count = Column(Integer, default=0)
    status = Column(String(50), default="discovered")
    local_path = Column(String(500), nullable=True)
    notes = Column(Text, default="")
    created_at = Column(Text, default="")
    updated_at = Column(Text, default="")


class ProjectModel(Base):
    """项目 ORM 模型。"""

    __tablename__ = "projects"

    id = Column(String(50), primary_key=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, default="")
    research_question = Column(Text, default="")
    hypothesis = Column(Text, default="")
    methodology = Column(Text, default="")
    keywords = Column(Text, default="")
    status = Column(String(50), default="draft")
    paper_ids = Column(Text, default="")
    outline = Column(Text, default="")
    created_at = Column(Text, default="")
    updated_at = Column(Text, default="")


# ---------------------------------------------------------------------------
# 引擎与会话管理
# ---------------------------------------------------------------------------

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """获取全局异步引擎单例。"""
    global _engine
    if _engine is None:
        settings = get_settings()
        settings.db_path.parent.mkdir(parents=True, exist_ok=True)
        _engine = create_async_engine(
            f"sqlite+aiosqlite:///{settings.db_path}",
            echo=False,
        )
        logger.info("SQLite 引擎已初始化: %s", settings.db_path)
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """获取会话工厂。"""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            get_engine(),
            expire_on_commit=False,
        )
    return _session_factory


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI 依赖：获取数据库会话。"""
    factory = get_session_factory()
    async with factory() as session:
        yield session


async def init_db() -> None:
    """初始化数据库表。"""
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("数据库表已初始化")
