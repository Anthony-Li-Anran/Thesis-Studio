"""Agent 团队配置领域模型。"""

from dataclasses import dataclass, field
from uuid import uuid4

AGENT_ROLES = ["researcher", "executor", "reviewer", "writer", "debater"]

WORKFLOW_API_DEFAULTS = [
    {
        "service_type": "arxiv",
        "name": "arXiv API",
        "endpoint": "https://export.arxiv.org/api/query",
        "test_url": "https://export.arxiv.org/api/query?search_query=all:test&max_results=1",
        "needs_key": False,
    },
    {
        "service_type": "semantic_scholar",
        "name": "Semantic Scholar",
        "endpoint": "https://api.semanticscholar.org/graph/v1",
        "test_url": "https://api.semanticscholar.org/graph/v1/paper/search?query=test&limit=1",
        "needs_key": True,
    },
]


@dataclass
class ExternalAPIConfig:
    """工作流 Agent 使用的外部 API 配置。"""

    service_type: str
    name: str
    endpoint: str
    test_url: str = ""
    needs_key: bool = False
    api_key: str = ""
    enabled: bool = True
    id: str = field(default_factory=lambda: uuid4().hex[:8])


@dataclass
class AIConfig:
    """单个 AI 配置，可绑定到多个 Agent 角色。"""

    name: str
    api_endpoint: str
    api_key: str
    model: str
    agents: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: uuid4().hex[:8])


@dataclass
class UserSettings:
    """用户全局设置，包含多个 AI 配置。"""

    user_id: str
    configs: list[AIConfig] = field(default_factory=list)
    external_apis: list[ExternalAPIConfig] = field(default_factory=list)
