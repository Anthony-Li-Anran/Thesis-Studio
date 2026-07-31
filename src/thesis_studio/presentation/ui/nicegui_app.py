"""NiceGUI 应用入口。

导入 home_page 即注册首页路由，main() 启动服务。
"""

from nicegui import ui

from ...config.settings import get_settings
from .home_page import home_page  # noqa: F401  注册首页路由


def main() -> None:
    """启动 NiceGUI 应用。"""
    settings = get_settings()
    ui.run(
        host=settings.api_host,
        port=8080,
        title="Thesis Studio",
        reload=True,
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
