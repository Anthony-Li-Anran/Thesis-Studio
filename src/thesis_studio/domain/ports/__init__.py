"""领域端口：定义基础设施层必须实现的接口（协议）。"""

from .embedding_port import EmbeddingProvider
from .llm_port import LLMProvider
from .repository_port import PaperRepository, ProjectRepository
from .search_port import LiteratureSearchProvider

__all__ = [
    "LLMProvider",
    "EmbeddingProvider",
    "PaperRepository",
    "ProjectRepository",
    "LiteratureSearchProvider",
]
