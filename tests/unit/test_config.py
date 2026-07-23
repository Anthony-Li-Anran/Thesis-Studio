"""配置模块测试。"""

import pytest

from thesisos.config import Settings


def test_default_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """默认配置应使用 Ollama 提供商。"""
    monkeypatch.delenv("THESISOS_LLM_PROVIDER", raising=False)
    monkeypatch.delenv("THESISOS_OLLAMA_MODEL", raising=False)
    settings = Settings()
    assert settings.llm_provider == "ollama"
    assert settings.ollama_model == "qwen2.5"
