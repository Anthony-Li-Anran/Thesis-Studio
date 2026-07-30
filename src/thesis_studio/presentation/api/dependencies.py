"""依赖注入容器。

组合根已移至 infrastructure.bootstrap，Presentation 层通过此模块获取服务。
"""

from ...infrastructure.bootstrap import (  # noqa: F401
    Services,
    get_analysis_service,
    get_literature_manage_service,
    get_literature_search_service,
    get_llm_provider,
    get_outline_service,
    get_paper_repo,
    get_project_repo,
    get_section_writer,
    get_services,
    get_text_polisher,
)

__all__ = [
    "Services",
    "get_analysis_service",
    "get_literature_manage_service",
    "get_literature_search_service",
    "get_llm_provider",
    "get_outline_service",
    "get_paper_repo",
    "get_project_repo",
    "get_section_writer",
    "get_services",
    "get_text_polisher",
]
