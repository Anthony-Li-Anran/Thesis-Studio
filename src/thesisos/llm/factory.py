"""LLM 提供商工厂。"""

from ..config import Settings, get_settings
from ..core.exceptions import ConfigError
from .base import LLMProvider
from .ollama import OllamaProvider


def create_llm(settings: Settings | None = None) -> LLMProvider:
    """根据配置创建 LLM 提供商实例。"""
    if settings is None:
        settings = get_settings()

    match settings.llm_provider:
        case "ollama":
            return OllamaProvider(settings.ollama_url, settings.ollama_model)
        case "openai":
            if not settings.openai_api_key:
                raise ConfigError("OpenAI API key 未配置")
            from .openai import OpenAIProvider

            return OpenAIProvider(settings.openai_api_key, settings.openai_model)
        case _:
            raise ConfigError(f"不支持的 LLM 提供商: {settings.llm_provider}")
