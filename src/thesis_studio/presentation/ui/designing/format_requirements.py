"""Format requirements drawer - slide-out panel for template selection and custom upload."""

from __future__ import annotations

from collections.abc import Callable
from contextlib import suppress
from typing import Any

from nicegui import ui

from ..i18n import t as _t

_DEFAULT_TEMPLATES: list[dict[str, str]] = [
    {"id": "imrad", "name": "IMRaD (理工科)", "desc": "绪论 - 文献综述 - 研究设计 - 预期结果 - 讨论 - 结论"},
    {"id": "humanities", "name": "五章式 (文科)", "desc": "绪论 - 文献综述 - 方法论 - 分析 - 结论"},
    {"id": "social_science", "name": "六章式 (社科)", "desc": "绪论 - 文献综述 - 理论框架 - 方法 - 结果 - 讨论"},
    {"id": "custom", "name": "自定义", "desc": "上传 Word/LaTeX/PDF 或输入文字描述"},
]


class FormatRequirementsDrawer:
    """Right-side drawer for format requirements management."""

    def __init__(self) -> None:
        self._selected_template: str = "imrad"
        self._custom_content: str = ""
        self._drawer: ui.element | None = None
        self._overlay: ui.element | None = None
        self._on_confirm: Callable[[str, str], None] | None = None
        self._is_open: bool = False

    def on_confirm(self, callback: Callable[[str, str], None]) -> None:
        self._on_confirm = callback

    def open(self) -> None:
        if self._is_open:
            return
        self._is_open = True
        self._build()

    def close(self) -> None:
        self._is_open = False
        if self._drawer is not None:
            with suppress(RuntimeError):
                self._drawer.delete()
                self._drawer = None
        if self._overlay is not None:
            with suppress(RuntimeError):
                self._overlay.delete()
                self._overlay = None

    def _build(self) -> None:
        self._overlay = ui.element("div").style(
            "position:fixed;top:0;left:0;right:0;bottom:0;"
            "background:rgba(0,0,0,0.4);z-index:999;"
            "transition:opacity 0.3s"
        )
        self._overlay.on("click", lambda: self.close())

        self._drawer = ui.element("div").style(
            "position:fixed;top:0;right:0;bottom:0;width:420px;"
            "z-index:1000;background:var(--bg-app);"
            "box-shadow:-4px 0 24px rgba(0,0,0,0.12);"
            "display:flex;flex-direction:column;"
            "transform:translateX(0);transition:transform 0.3s"
        )

        with self._drawer:
            self._build_header()
            self._build_body()

    def _build_header(self) -> None:
        with ui.element("div").classes(
            "flex items-center justify-between px-5 py-4 border-b ts-border-divider"
        ):
            ui.label(_t("designing.format_requirements")).classes("text-base font-semibold ts-text-nav")
            btn = ui.element("button").classes(
                "ts-btn-tertiary inline-flex items-center justify-center"
                " rounded-full h-[32px] w-[32px]"
            )
            btn.on("click", lambda: self.close())
            with btn:
                ui.html('<svg fill="currentColor" width="16" height="16" viewBox="0 0 20 20"><path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z"/></svg>')

    def _build_body(self) -> None:
        with ui.element("div").classes("flex-1 overflow-y-auto px-5 py-4 space-y-5"):
            ui.label(_t("designing.select_template")).classes("text-sm font-medium ts-text-nav")

            for tpl in _DEFAULT_TEMPLATES:
                self._build_template_card(tpl)

            ui.separator().classes("my-3")

            self._build_custom_section()

            # Constraint preview
            ui.separator().classes("my-3")
            ui.label(_t("designing.current_constraints")).classes("text-sm font-medium ts-text-nav")
            self._build_constraints_preview()

        # Footer
        with ui.element("div").classes("px-5 py-4 border-t ts-border-divider"):
            with ui.element("div").classes("flex gap-3"):
                ui.button(_t("designing.cancel"), on_click=lambda: self.close()).classes("ts-btn-secondary flex-1").props("no-caps")
                ui.button(_t("designing.apply"), on_click=lambda: self._handle_confirm()).classes("ts-btn-primary flex-1").props("no-caps")

    def _build_template_card(self, tpl: dict[str, str]) -> None:
        is_active = self._selected_template == tpl["id"]
        with ui.element("div").classes(
            f"rounded-xl p-4 border cursor-pointer transition-all {'ts-bg-input border-blue-500' if is_active else 'ts-bg-sidepanel ts-border-divider hover:ts-bg-input'}"
        ).on("click", lambda _t=tpl["id"]: self._select_template(_t)):
            with ui.element("div").classes("flex items-center justify-between"):
                ui.label(tpl["name"]).classes("text-sm font-medium ts-text-nav")
                if is_active:
                    ui.element("div").classes("w-4 h-4 rounded-full ts-bg-input").style("border:2px solid #3b82f6;background:#3b82f6")
                else:
                    ui.element("div").classes("w-4 h-4 rounded-full border-2 ts-border-divider")
            ui.label(tpl["desc"]).classes("text-xs ts-text-secondary mt-1")

    def _select_template(self, template_id: str) -> None:
        self._selected_template = template_id
        self._rebuild()

    def _build_custom_section(self) -> None:
        with ui.element("div").classes("space-y-2"):
            ui.label(_t("designing.custom_upload")).classes("text-xs font-medium ts-text-nav")
            ta = ui.textarea(
                placeholder=_t("designing.upload_hint"),
                value=self._custom_content,
            ).classes("w-full").style("min-height:80px;font-size:12px").props("autogrow")
            ta.on("update:model-value", self._handle_custom_change)

            with ui.element("div").classes("flex gap-2"):
                ui.button(icon="upload_file", on_click=lambda: ui.notify(_t("designing.upload_todo"))).props("flat round dense").tooltip(_t("designing.upload_file"))
                ui.button(icon="description", on_click=lambda: ui.notify(_t("designing.upload_todo"))).props("flat round dense").tooltip(_t("designing.paste_text"))

    def _handle_custom_change(self, e: Any) -> None:
        self._custom_content = str(e.args) if e.args else ""

    def _build_constraints_preview(self) -> None:
        with ui.element("div").classes("ts-bg-sidepanel rounded-xl p-4 space-y-2"):
            constraints = self._get_constraints()
            for c in constraints:
                with ui.element("div").classes("flex items-center gap-2"):
                    ui.element("div").classes("w-1.5 h-1.5 rounded-full").style("background:var(--text-nav-primary)")
                    ui.label(c).classes("text-xs ts-text-secondary")

    def _get_constraints(self) -> list[str]:
        if self._selected_template == "imrad":
            return [
                _t("designing.constraint_chapters").format(count=6),
                _t("designing.constraint_imrad"),
                _t("designing.constraint_ref_format"),
            ]
        elif self._selected_template == "humanities":
            return [
                _t("designing.constraint_chapters").format(count=5),
                _t("designing.constraint_humanities"),
            ]
        elif self._selected_template == "social_science":
            return [
                _t("designing.constraint_chapters").format(count=6),
                _t("designing.constraint_social"),
            ]
        else:
            return [_t("designing.constraint_custom")]

    def _handle_confirm(self) -> None:
        if self._on_confirm:
            self._on_confirm(self._selected_template, self._custom_content)
        self.close()

    def _rebuild(self) -> None:
        if self._drawer is not None:
            with suppress(RuntimeError):
                self._drawer.clear()
                with self._drawer:
                    self._build_header()
                    self._build_body()
