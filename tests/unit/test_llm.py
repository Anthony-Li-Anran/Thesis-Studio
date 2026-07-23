"""LLM 模块测试。"""

from thesisos.config import Settings
from thesisos.domain.ports.llm_port import LLMProvider
from thesisos.infrastructure.llm.factory import LLMFactory
from thesisos.infrastructure.llm.ollama_adapter import OllamaAdapter


def test_create_llm_ollama() -> None:
    """默认配置应创建 OllamaAdapter。"""
    settings = Settings(llm_provider="ollama")
    provider = LLMFactory(settings).create()
    assert isinstance(provider, OllamaAdapter)


def test_ollama_provider_satisfies_protocol() -> None:
    """OllamaAdapter 应满足 LLMProvider 协议。"""
    provider = OllamaAdapter("http://localhost:11434", "qwen2.5")
    assert isinstance(provider, LLMProvider)
