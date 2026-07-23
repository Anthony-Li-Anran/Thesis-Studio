"""领域异常层级。所有业务异常继承 ThesisOSError。"""


class ThesisOSError(Exception):
    """所有 ThesisOS 领域异常的基类。"""


class ConfigError(ThesisOSError):
    """配置相关错误。"""


class LLMError(ThesisOSError):
    """LLM 调用相关错误。"""


class LLMUnavailableError(LLMError):
    """LLM 服务不可用（如 Ollama 未启动）。"""


class DatabaseError(ThesisOSError):
    """数据库操作相关错误。"""


class WorkflowError(ThesisOSError):
    """工作流执行相关错误。"""
