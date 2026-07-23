"""领域实体与值对象。纯 Python 数据类，不依赖 ORM。"""

from .paper import Paper, PaperStatus
from .project import Project, ProjectStatus
from .search import SearchQuery, SearchResult

__all__ = [
    "Paper",
    "PaperStatus",
    "Project",
    "ProjectStatus",
    "SearchQuery",
    "SearchResult",
]
