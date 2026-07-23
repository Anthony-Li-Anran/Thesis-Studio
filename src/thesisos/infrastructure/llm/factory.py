"""LLM 适配器工厂。根据配置创建对应的 LLMProvider 实现。"""

from ...config.settings import Settings, get_settings
from ...domain.exceptions import ConfigError
from ...domain.ports.llm_port import LLMProvider
from .ollama_adapter import OllamaAdapter
from .openai_adapter import OpenAIAdapter


class LLMFactory:
    """LLM 适配器工厂。支持注册新提供商而不修改已有代码（开闭原则）。"""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    def create(self) -> LLMProvider:
        """根据配置创建 LLM 提供商实例。"""
        match self._settings.llm_provider:
            case "ollama":
                return OllamaAdapter(
                    url=self._settings.ollama_url,
                    model=self._settings.ollama_model,
                )
            case "openai":
                if not self._settings.openai_api_key:
                    raise ConfigError("OpenAI API key 未配置")
                return OpenAIAdapter(
                    api_key=self._settings.openai_api_key,
                    model=self._settings.openai_model,
                )
            case _:
                raise ConfigError(f"不支持的 LLM 提供商: {self._settings.llm_provider}")
