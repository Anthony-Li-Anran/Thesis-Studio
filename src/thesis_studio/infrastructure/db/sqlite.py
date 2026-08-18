"""SQLite database engine, ORM models, and session management."""

from __future__ import annotations

from typing import Any

import asyncio
import threading
from pathlib import Path

from sqlalchemy import Column, Integer, String, Text, inspect, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from ..logging import get_logger

logger = get_logger(__name__)

DB_PATH = Path(__file__).resolve().parent.parent.parent.parent.parent / "data" / "thesis_studio.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

_engine = create_async_engine(
    f"sqlite+aiosqlite:///{DB_PATH}",
    echo=False,
    connect_args={"check_same_thread": False},
)
_async_session_factory = async_sessionmaker(_engine, expire_on_commit=False)
_lock = threading.Lock()


class Base(DeclarativeBase):
    pass


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
    project_id = Column(String(50), default="", index=True)
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
    exploring_state = Column(Text, default="")  # JSON: EXPLORING session state
    created_at = Column(Text, default="")
    updated_at = Column(Text, default="")


class UserModel(Base):
    """User ORM model."""

    __tablename__ = "users"

    id = Column(String(50), primary_key=True)
    email = Column(String(200), nullable=False, unique=True, index=True)
    password_hash = Column(String(200), nullable=False)
    name = Column(String(100), default="")
    created_at = Column(Text, default="")


class UserSettingsModel(Base):
    """User settings ORM model."""

    __tablename__ = "user_settings"

    user_id = Column(String(50), primary_key=True)
    settings_json = Column(Text, default="")


def get_engine() -> Any:
    return _engine


def get_session_factory() -> Any:
    return _async_session_factory


def get_session() -> Any:
    """Create a new async session (convenience)."""
    return _async_session_factory()


async def _ensure_column(table_name: str, column_name: str, column_type: str) -> None:
    """Ensure a column exists in the table, add it if missing."""
    async with _engine.begin() as conn:

        def _check(connection: Any) -> bool:
            insp = inspect(connection)
            cols = {c["name"] for c in insp.get_columns(table_name)}
            return column_name in cols

        exists = await conn.run_sync(_check)
        if not exists:
            await conn.execute(
                text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
            )
            logger.info("Added column %s to %s", column_name, table_name)


async def init_db() -> None:
    """Initialize database tables and migrate as needed."""
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Ensure new columns exist on existing tables
    await _ensure_column("projects", "exploring_state", "TEXT DEFAULT ''")
    await _ensure_column("papers", "project_id", "TEXT DEFAULT ''")
    logger.info("Database tables initialized")
