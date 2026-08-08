"""SQLite async engine, ORM models, and session management."""

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
# ORM base and models (internal infrastructure, not exposed to domain)
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    """Base class for all ORM models."""


class PaperModel(Base):
    """Paper ORM model."""

    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False, index=True)
    authors = Column(Text, default="")  # JSON-encoded list
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
    """Project ORM model."""

    __tablename__ = "projects"

    id = Column(String(50), primary_key=True)
    user_id = Column(String(50), default="", index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, default="")
    research_question = Column(Text, default="")
    hypothesis = Column(Text, default="")
    methodology = Column(Text, default="")
    keywords = Column(Text, default="")
    status = Column(String(50), default="init")
    paper_ids = Column(Text, default="")
    outline = Column(Text, default="")
    created_at = Column(Text, default="")
    updated_at = Column(Text, default="")


class UserModel(Base):
    """User ORM model."""

    __tablename__ = "users"

    id = Column(String(50), primary_key=True)
    email = Column(String(200), nullable=False, unique=True, index=True)
    name = Column(String(100), default="")
    password_hash = Column(Text, default="")
    created_at = Column(Text, default="")
class UserSettingsModel(Base):
    """User settings ORM model. JSON stored in TEXT column."""

    __tablename__ = "user_settings"

    user_id = Column(String(50), primary_key=True)
    settings_json = Column(Text, default="")

# ---------------------------------------------------------------------------
# Engine and session management
# ---------------------------------------------------------------------------

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Get global async engine singleton."""
    global _engine
    if _engine is None:
        settings = get_settings()
        settings.db_path.parent.mkdir(parents=True, exist_ok=True)
        _engine = create_async_engine(
            f"sqlite+aiosqlite:///{settings.db_path}",
            echo=False,
        )
        logger.info("SQLite engine initialized: %s", settings.db_path)
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get session factory."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            get_engine(),
            expire_on_commit=False,
        )
    return _session_factory


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency: get database session."""
    factory = get_session_factory()
    async with factory() as session:
        yield session


async def init_db() -> None:
    """Initialize database tables."""
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized")

