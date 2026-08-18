"""LLM adapter factory. Registry pattern, add providers without touching existing code (OCP)."""

from collections.abc import Callable
from typing import ClassVar

from ...config.settings import Settings, get_settings
from ...domain.exceptions import ConfigError
from ...domain.models.settings import AIConfig
from ...domain.ports.llm_port import LLMProvider
from .ollama_adapter import OllamaAdapter
from .openai_adapter import OpenAIAdapter

LLMCreator = Callable[[Settings], LLMProvider]


def _create_ollama(settings: Settings) -> LLMProvider:
    """Create Ollama adapter."""
    return OllamaAdapter(url=settings.ollama_url, model=settings.ollama_model)


def _create_deepseek(settings: Settings) -> LLMProvider:
    """Create Deepseek adapter (OpenAI-compatible)."""
    key = settings.deepseek_api_key or settings.openai_api_key
    if not key:
        raise ConfigError("Deepseek API key required")
    return OpenAIAdapter(
        api_key=key,
        model=settings.deepseek_model,
        base_url=settings.deepseek_base_url,
    )


def _create_openai(settings: Settings) -> LLMProvider:
    """Create OpenAI adapter."""
    if not settings.openai_api_key:
        raise ConfigError("OpenAI API key required")
    return OpenAIAdapter(api_key=settings.openai_api_key, model=settings.openai_model)


class LLMFactory:
    """LLM adapter factory. Extensible via registry."""

    _registry: ClassVar[dict[str, LLMCreator]] = {
        "ollama": _create_ollama,
        "openai": _create_openai,
        "deepseek": _create_deepseek,
    }

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    @classmethod
    def register(cls, name: str, creator: LLMCreator) -> None:
        """Register a new LLM provider."""
        cls._registry[name] = creator

    def create(self) -> LLMProvider:
        """Create LLM provider from .env settings."""
        provider_name = self._settings.llm_provider
        creator = self._registry.get(provider_name)
        if creator is None:
            raise ConfigError(f"Unsupported LLM provider: {provider_name}")
        return creator(self._settings)

    @staticmethod
    def create_from_config(config: AIConfig) -> LLMProvider:
        """Create LLM provider from a user-saved AIConfig.

        Detects local vs cloud by endpoint pattern:
        - localhost / 127.0.0.1 → OllamaAdapter
        - everything else → OpenAIAdapter (OpenAI-compatible API)
        """
        endpoint = config.api_endpoint.strip()
        is_local = any(
            host in endpoint
            for host in ("localhost", "127.0.0.1", "0.0.0.0", "ollama")
        )
        if is_local:
            base = endpoint.rstrip("/").rstrip("/v1")
            url = base if "/api" in base else f"{base}/api"
            return OllamaAdapter(url=url, model=config.model)
        return OpenAIAdapter(
            api_key=config.api_key,
            model=config.model,
            base_url=endpoint,
        )
