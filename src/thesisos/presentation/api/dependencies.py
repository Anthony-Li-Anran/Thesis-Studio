"""依赖注入容器（兼容重导出）。

组合根已移至 infrastructure.bootstrap，Presentation 层通过此模块获取服务。
"""

from ...infrastructure.bootstrap import (  # noqa: F401
    Services,
    get_analysis_service,
    get_literature_manage_service,
    get_literature_search_service,
    get_llm_provider,
    get_paper_repo,
    get_project_repo,
    get_services,
    get_writing_service,
)
