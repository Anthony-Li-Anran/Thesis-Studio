"""领域模型模块——纯 Python 数据类，不依赖 ORM。"""

from .paper import Paper, PaperStatus
from .project import Project, ProjectStatus
from .search import SearchQuery, SearchResult
from .user import User
from .settings import AIConfig, AGENT_ROLES, UserSettings

__all__ = [
    "Paper",
    "PaperStatus",
    "Project",
    "ProjectStatus",
    "SearchQuery",
    "SearchResult",
    "User",
    "AIConfig",
    "AGENT_ROLES",
    "UserSettings",
]
