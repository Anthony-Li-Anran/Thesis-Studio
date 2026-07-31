"""组合根（Composition Root）：组装基础设施依赖。

Clean Architecture 规定组合根应在最外层——这里放在 infrastructure/bootstrap/，
因为它是唯一知道所有具体实现的模块。Presentation 层通过抽象接口获取依赖。
"""

from functools import lru_cache

from ...config.settings import get_settings
from ...domain.ports.llm_port import LLMProvider
from ...domain.ports.repository_port import PaperRepository, ProjectRepository
from ..db.repositories import SQLitePaperRepository, SQLiteProjectRepository
from ..llm.factory import LLMFactory


@lru_cache
def get_llm_provider() -> LLMProvider:
    """获取 LLM 提供商（单例）。"""
    return LLMFactory(get_settings()).create()


@lru_cache
def get_paper_repo() -> PaperRepository:
    """获取论文存储（单例）。"""
    return SQLitePaperRepository()


@lru_cache
def get_project_repo() -> ProjectRepository:
    """获取项目存储（单例）。"""
    return SQLiteProjectRepository()
