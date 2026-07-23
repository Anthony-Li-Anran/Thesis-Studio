"""LLM 适配器。"""

from .factory import LLMFactory
from .ollama_adapter import OllamaAdapter
from .openai_adapter import OpenAIAdapter

__all__ = [
    "OllamaAdapter",
    "OpenAIAdapter",
    "LLMFactory",
]
