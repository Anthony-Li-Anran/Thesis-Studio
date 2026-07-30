"""领域异常层级。所有业务异常继承 ThesisStudioError。"""


class ThesisStudioError(Exception):
    """所有 Thesis Studio 领域异常的基类。"""


class ConfigError(ThesisStudioError):
    """配置相关错误。"""


class LLMError(ThesisStudioError):
    """LLM 调用相关错误。"""


class LLMUnavailableError(LLMError):
    """LLM 服务不可用（如 Ollama 未启动）。"""


class LLMRateLimitError(LLMError):
    """LLM API 速率限制。"""


class LLMTokenLimitError(LLMError):
    """LLM Token 超限。"""


class DatabaseError(ThesisStudioError):
    """数据库操作相关错误。"""


class WorkflowError(ThesisStudioError):
    """工作流执行相关错误。"""


class LiteratureError(ThesisStudioError):
    """文献检索相关错误。"""


class AnalysisError(ThesisStudioError):
    """数据分析相关错误。"""


class WritingError(ThesisStudioError):
    """论文撰写相关错误。"""


class ValidationError(ThesisStudioError):
    """领域验证错误。"""
