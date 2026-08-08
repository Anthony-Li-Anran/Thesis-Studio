"""应用配置，从 .env 与环境变量读取。"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """配置项，环境变量前缀 THESIS_STUDIO_。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="THESIS_STUDIO_",
        env_file_encoding="utf-8",
    )

    # LLM
    llm_provider: Literal["ollama", "openai"] = "ollama"
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o"

    # 存储
    db_path: Path = Path("data/thesis_studio.db")
    chroma_path: Path = Path("data/chroma")

    # 服务
    api_host: str = "127.0.0.1"
    api_port: int = 8000

    # NiceGUI 会话存储密钥
    storage_secret: str = "thesis-studio-local-dev-secret"

    # 外部 API
    semantic_scholar_api_key: str | None = None


@lru_cache
def get_settings() -> Settings:
    """获取配置单例。"""
    return Settings()
