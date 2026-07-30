"""NiceGUI 管理面板。"""

from nicegui import ui

from ...config.settings import get_settings


def build_ui() -> None:
    """构建管理面板界面。"""
    ui.label("Thesis Studio 管理面板").classes("text-h4")

    with ui.row():
        ui.button("文献库", on_click=lambda: ui.notify("文献库功能开发中"))
        ui.button("项目进度", on_click=lambda: ui.notify("项目进度功能开发中"))
        ui.button("数据分析", on_click=lambda: ui.notify("数据分析功能开发中"))
        ui.button("设置", on_click=lambda: ui.notify("设置功能开发中"))


def main() -> None:
    """启动管理面板。"""
    build_ui()
    settings = get_settings()
    ui.run(port=8080, host=settings.api_host)
