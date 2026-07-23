"""全局配置，从 .env 文件加载。"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """全局配置。从 .env 文件加载，环境变量前缀 THESISOS_。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="THESISOS_",
        env_file_encoding="utf-8",
    )

    # LLM
    llm_provider: Literal["ollama", "openai"] = "ollama"
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o"

    # 数据库
    db_path: Path = Path("data/thesisos.db")
    chroma_path: Path = Path("data/chroma")

    # 服务
    api_host: str = "127.0.0.1"
    api_port: int = 8000

    # 文献检索
    semantic_scholar_api_key: str | None = None


@lru_cache
def get_settings() -> Settings:
    """获取全局配置单例。"""
    return Settings()
