"""NiceGUI 管理面板。"""

from nicegui import ui

from ..config import get_settings


def build_ui() -> None:
    """构建管理面板界面。"""
    ui.label("ThesisOS 管理面板").classes("text-h4")
    with ui.row():
        ui.button("文献库")
        ui.button("项目进度")
        ui.button("数据分析")
        ui.button("设置")


def main() -> None:
    """启动管理面板。"""
    build_ui()
    settings = get_settings()
    ui.run(port=8080, host=settings.api_host)
