"""LLM 模块测试。"""

from thesisos.config import Settings
from thesisos.llm import LLMProvider, create_llm
from thesisos.llm.ollama import OllamaProvider


def test_create_llm_ollama() -> None:
    """默认配置应创建 OllamaProvider。"""
    settings = Settings(llm_provider="ollama")
    provider = create_llm(settings)
    assert isinstance(provider, OllamaProvider)


def test_ollama_provider_satisfies_protocol() -> None:
    """OllamaProvider 应满足 LLMProvider 协议。"""
    provider = OllamaProvider("http://localhost:11434", "qwen2.5")
    assert isinstance(provider, LLMProvider)
