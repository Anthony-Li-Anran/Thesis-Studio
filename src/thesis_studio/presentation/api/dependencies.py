"""依赖注入容器。

组合根已移至 infrastructure.bootstrap，Presentation 层通过此模块获取依赖。
"""

from ...infrastructure.bootstrap import (  # noqa: F401
    get_llm_provider,
    get_paper_repo,
    get_project_repo,
)

__all__ = [
    "get_llm_provider",
    "get_paper_repo",
    "get_project_repo",
]
