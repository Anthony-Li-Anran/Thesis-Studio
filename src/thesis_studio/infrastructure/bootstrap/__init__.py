"""Composition Root: dependency injection entry point.
Clean Architecture requires upper layers to depend on abstractions.
All concrete implementations are assembled under infrastructure/bootstrap/.
Presentation layer obtains assembled dependencies from here."""

from functools import lru_cache

from ...config.settings import get_settings
from ...domain.ports.auth_port import AuthProvider
from ...domain.ports.llm_port import LLMProvider
from ...domain.ports.repository_port import PaperRepository, ProjectRepository
from ..auth.local_provider import LocalAuthProvider
from ..db.repositories import (
    GuestProjectRepository,
    GuestSettingsRepository,
    SQLitePaperRepository,
    SQLiteProjectRepository,
    SQLiteSettingsRepository,
)
from ..llm.factory import LLMFactory


@lru_cache
def get_llm_provider() -> LLMProvider:
    """Get LLM provider singleton from .env settings."""
    return LLMFactory(get_settings()).create()


async def get_llm_for_agent(agent_name: str = "researcher") -> LLMProvider:
    """Resolve LLM provider from user's settings card configs.

    Looks up the AIConfig assigned to the given agent role.
    Falls back to .env defaults if no config found.
    """
    repo = get_current_user_settings_repo()
    try:
        from nicegui import app
        user_id = app.storage.user.get("user_id", "")
        is_guest = app.storage.user.get("is_guest", False)
    except RuntimeError:
        user_id = ""
        is_guest = False
    uid = "guest" if is_guest else (user_id or "")
    settings = await repo.get(uid)
    for cfg in settings.configs:
        if agent_name in cfg.agents:
            return LLMFactory.create_from_config(cfg)
    return get_llm_provider()


@lru_cache
def get_paper_repo() -> PaperRepository:
    """Get paper repository singleton."""
    return SQLitePaperRepository()


@lru_cache
def get_project_repo() -> ProjectRepository:
    return SQLiteProjectRepository()


_guest_repo: GuestProjectRepository | None = None
_guest_settings_repo: GuestSettingsRepository | None = None


def _get_guest_repo() -> GuestProjectRepository:
    global _guest_repo
    if _guest_repo is None:
        _guest_repo = GuestProjectRepository()
    return _guest_repo


def _get_guest_settings_repo() -> GuestSettingsRepository:
    global _guest_settings_repo
    if _guest_settings_repo is None:
        _guest_settings_repo = GuestSettingsRepository()
    return _guest_settings_repo


def get_current_user_repo() -> ProjectRepository:
    from nicegui import app
    try:
        is_guest = app.storage.user.get("is_guest", False)
        user_id = app.storage.user.get("user_id", "")
    except RuntimeError:
        is_guest = False
        user_id = ""
    if is_guest:
        return _get_guest_repo()
    return SQLiteProjectRepository(user_id=user_id)


def get_current_user_id() -> str:
    from nicegui import app
    try:
        uid = app.storage.user.get("user_id", "")
        is_guest = app.storage.user.get("is_guest", False)
    except RuntimeError:
        return ""
    return "" if is_guest else (uid or "")


def get_current_user_settings_repo():
    from nicegui import app
    try:
        is_guest = app.storage.user.get("is_guest", False)
        user_id = app.storage.user.get("user_id", "")
    except RuntimeError:
        is_guest = False
        user_id = ""
    if is_guest:
        return _get_guest_settings_repo()
    return SQLiteSettingsRepository(user_id=user_id)


def clear_guest_projects() -> None:
    global _guest_repo, _guest_settings_repo
    if _guest_repo is not None:
        _guest_repo.clear()
        _guest_repo = None
    if _guest_settings_repo is not None:
        _guest_settings_repo.clear()
        _guest_settings_repo = None


@lru_cache
def get_auth_provider() -> AuthProvider:
    return LocalAuthProvider()
