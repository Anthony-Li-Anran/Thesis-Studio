"""领域异常层次。所有异常继承自 ThesisStudioError。"""


class ThesisStudioError(Exception):
    """Thesis Studio 所有异常的基类。"""


class ConfigError(ThesisStudioError):
    """配置缺失或非法。"""


class LLMError(ThesisStudioError):
    """LLM 调用失败。"""


class LLMUnavailableError(LLMError):
    """LLM 不可用，如 Ollama 未启动。"""


class LLMRateLimitError(LLMError):
    """LLM API 触发限流。"""


class LLMTokenLimitError(LLMError):
    """LLM 超出 Token 上限。"""


class DatabaseError(ThesisStudioError):
    """数据库读写异常。"""


class WorkflowError(ThesisStudioError):
    """工作流编排异常。"""


class LiteratureError(ThesisStudioError):
    """文献检索异常。"""


class AnalysisError(ThesisStudioError):
    """分析阶段异常。"""


class WritingError(ThesisStudioError):
    """写作阶段异常。"""


class ValidationError(ThesisStudioError):
    """输入校验失败。"""


class AuthError(ThesisStudioError):
    """认证授权异常。"""


class AuthConflictError(AuthError):
    """注册冲突，如邮箱已存在。"""


class AuthCredentialError(AuthError):
    """登录凭据无效。"""
