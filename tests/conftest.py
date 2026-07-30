"""pytest 全局 fixtures。"""

from pathlib import Path

import pytest

from thesis_studio.config import Settings, get_settings


@pytest.fixture(autouse=True)
def clear_settings_cache() -> None:
    """每个测试前清除配置缓存，确保隔离。"""
    get_settings.cache_clear()


@pytest.fixture
def test_settings(tmp_path: Path) -> Settings:
    """返回临时路径的测试配置。"""
    return Settings(
        db_path=tmp_path / "test.db",
        chroma_path=tmp_path / "chroma",
    )
