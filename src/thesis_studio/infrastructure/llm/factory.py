"""LLM 适配器工厂。基于注册表模式，新增提供商无需修改已有代码（开闭原则）。"""

from collections.abc import Callable
from typing import ClassVar

from ...config.settings import Settings, get_settings
from ...domain.exceptions import ConfigError
from ...domain.ports.llm_port import LLMProvider
from .ollama_adapter import OllamaAdapter
from .openai_adapter import OpenAIAdapter

# 类型别名：提供商构造函数，接收 Settings 返回 LLMProvider
LLMCreator = Callable[[Settings], LLMProvider]


def _create_ollama(settings: Settings) -> LLMProvider:
    """创建 Ollama 适配器。"""
    return OllamaAdapter(url=settings.ollama_url, model=settings.ollama_model)


def _create_openai(settings: Settings) -> LLMProvider:
    """创建 OpenAI 适配器。"""
    if not settings.openai_api_key:
        raise ConfigError("OpenAI API key 需配置")
    return OpenAIAdapter(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
    )


class LLMFactory:
    """LLM 适配器工厂。通过注册表支持扩展，新增提供商只需 register。"""

    _registry: ClassVar[dict[str, LLMCreator]] = {
        "ollama": _create_ollama,
        "openai": _create_openai,
    }

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    @classmethod
    def register(cls, name: str, creator: LLMCreator) -> None:
        """注册新的 LLM 提供商构造函数。"""
        cls._registry[name] = creator

    def create(self) -> LLMProvider:
        """根据配置创建 LLM 提供商实例。"""
        provider_name = self._settings.llm_provider
        creator = self._registry.get(provider_name)
        if creator is None:
            raise ConfigError(f"不支持的 LLM 提供商: {provider_name}")
        return creator(self._settings)
