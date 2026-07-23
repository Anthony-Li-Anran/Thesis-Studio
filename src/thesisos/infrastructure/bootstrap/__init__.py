"""组合根（Composition Root）：组装所有服务及其依赖。

Clean Architecture 规定组合根应在最外层——这里放在 infrastructure/bootstrap/，
因为它是唯一知道所有具体实现的模块。Presentation 层通过抽象接口获取服务。
"""

from functools import lru_cache

from ...application.analysis import AnalysisService
from ...application.literature.manage_service import LiteratureManageService
from ...application.literature.search_service import LiteratureSearchService
from ...application.writing import WritingService
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
    """获取论文仓储（单例）。"""
    return SQLitePaperRepository()


@lru_cache
def get_project_repo() -> ProjectRepository:
    """获取项目仓储（单例）。"""
    return SQLiteProjectRepository()


def get_literature_search_service() -> LiteratureSearchService:
    """创建文献检索服务。"""
    return LiteratureSearchService(
        search_providers=[],  # TODO: Phase 2 添加实际检索适配器
        paper_repo=get_paper_repo(),
    )


def get_literature_manage_service() -> LiteratureManageService:
    """创建文献管理服务。"""
    return LiteratureManageService(
        paper_repo=get_paper_repo(),
        llm=get_llm_provider(),
    )


def get_analysis_service() -> AnalysisService:
    """创建数据分析服务。"""
    return AnalysisService(llm=get_llm_provider())


def get_writing_service() -> WritingService:
    """创建论文撰写服务。"""
    return WritingService(
        llm=get_llm_provider(),
        project_repo=get_project_repo(),
        paper_repo=get_paper_repo(),
    )


class Services:
    """服务容器，集中管理所有用例服务。"""

    @property
    def literature_search(self) -> LiteratureSearchService:
        return get_literature_search_service()

    @property
    def literature_manage(self) -> LiteratureManageService:
        return get_literature_manage_service()

    @property
    def analysis(self) -> AnalysisService:
        return get_analysis_service()

    @property
    def writing(self) -> WritingService:
        return get_writing_service()


@lru_cache
def get_services() -> Services:
    """获取服务容器（单例）。"""
    return Services()
