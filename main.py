"""Thesis Studio 启动入口。"""

from nicegui import app, ui

from thesis_studio.config import get_settings
from thesis_studio.infrastructure.db import init_db
from thesis_studio.presentation.ui.home_page import home_page  # noqa: F401


@app.on_startup
async def _init_database() -> None:
    """启动时初始化数据库表。"""
    await init_db()


settings = get_settings()
ui.run(
    host=settings.api_host,
    port=settings.api_port,
    title="Thesis Studio",
    reload=True,
    storage_secret=settings.storage_secret,
)
