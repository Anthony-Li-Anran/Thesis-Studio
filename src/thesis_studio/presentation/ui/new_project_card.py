"""新建项目对话框。四字段表单 + Create 持久化，复用共享 dialog 设计系统。"""

from nicegui import ui

from ...domain.models.project import Project
from ...infrastructure.bootstrap import get_current_user_id, get_current_user_repo
from .i18n import t

_CLOSE_ICON = (
    '<svg fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" '
    'width="18" height="18" xmlns="http://www.w3.org/2000/svg">'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>'
)

_X_ICON = (
    '<svg fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" '
    'width="12" height="12" xmlns="http://www.w3.org/2000/svg">'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>'
)


def new_project_card() -> ui.dialog:
    """创建新建项目对话框，返回 dialog 供外部 open()。"""
    state: dict = {"keywords": []}
    with ui.dialog() as dialog:
        with ui.element("div").classes("ts-dialog-card").style("width:600px;max-width:92vw"):
            with ui.element("div").classes("ts-dialog-body relative"):
                _close_button(dialog)
                with ui.element("div").classes("ts-dialog-header"):
                    ui.label(t("new_project.title")).classes("ts-dialog-title")
                    ui.label(t("new_project.subtitle")).classes("ts-dialog-subtitle")
                with ui.element("div").classes("ts-dialog-form"):
                    fields = _form(state)
                error_label = ui.label("").classes("ts-dialog-error")

                async def _create() -> None:
                    await _on_create(state, dialog, fields, error_label)

                _footer(dialog, _create)
    return dialog


def _close_button(dialog: ui.dialog) -> None:
    """右上角关闭按钮。"""
    btn = ui.element("div").classes("ts-dialog-close")
    btn.on("click", dialog.close)
    with btn:
        ui.html(_CLOSE_ICON)


def _form(state: dict) -> dict:
    """渲染四字段，返回控件引用。"""
    title = _field(t("new_project.field.title"), t("new_project.ph.title"))
    question = _field(t("new_project.field.question"), t("new_project.ph.question"), textarea=True)
    _keyword_field(state)
    description = _field(
        t("new_project.field.description"), t("new_project.ph.description"), textarea=True
    )
    return {"title": title, "question": question, "description": description}


def _field(label: str, placeholder: str, textarea: bool = False) -> ui.input:
    """单个带标签的输入字段。"""
    with ui.element("div").classes("ts-dialog-field"):
        ui.label(label).classes("ts-dialog-label")
        cls = "ts-dialog-input ts-dialog-textarea w-full" if textarea else "ts-dialog-input w-full"
        widget = (
            ui.textarea(placeholder=placeholder) if textarea else ui.input(placeholder=placeholder)
        )
        return widget.classes(cls).props("dark dense")


def _keyword_field(state: dict) -> None:
    """关键词输入 + 标签 chips，回车添加。"""
    with ui.element("div").classes("ts-dialog-field"):
        ui.label(t("new_project.field.keywords")).classes("ts-dialog-label")
        kw_input = (
            ui.input(placeholder=t("new_project.ph.keywords"))
            .classes("ts-dialog-input w-full")
            .props("dark dense")
        )
        chips = ui.element("div").classes("ts-kw-chips")

        def _render() -> None:
            chips.clear()
            with chips:
                for kw in state["keywords"]:
                    _chip(state, kw, _render)

        def _add(_: object) -> None:
            val = kw_input.value.strip()
            if val and val not in state["keywords"]:
                state["keywords"].append(val)
                kw_input.value = ""
                _render()

        kw_input.on("keydown.enter", _add)
        _render()


def _chip(state: dict, kw: str, on_change) -> None:
    """单个关键词标签，含移除按钮。"""
    with ui.element("div").classes("ts-kw-chip"):
        ui.label(kw)
        btn = ui.element("button").classes("ts-kw-chip-x")

        def _remove(_: object) -> None:
            state["keywords"].remove(kw)
            on_change()

        btn.on("click", _remove)
        with btn:
            ui.html(_X_ICON)


def _footer(dialog: ui.dialog, on_create) -> None:
    """底部取消/创建按钮。"""
    with ui.element("div").classes("ts-dialog-footer"):
        ui.button(t("new_project.cancel")).classes("ts-btn-secondary").props(
            "unelevated no-caps"
        ).on("click", dialog.close)
        ui.button(t("new_project.create")).classes("ts-btn-primary").props("unelevated no-caps").on(
            "click", on_create
        )


async def _on_create(state: dict, dialog: ui.dialog, fields: dict, error_label: ui.label) -> None:
    """校验标题必填，持久化项目后关闭刷新。"""
    title = fields["title"].value.strip()
    if not title:
        error_label.text = t("new_project.title_required")
        return
    project = Project(
        title=title,
        research_question=fields["question"].value.strip(),
        description=fields["description"].value.strip(),
        keywords=list(state["keywords"]),
    )
    try:
        project.user_id = get_current_user_id()
        await get_current_user_repo().add(project)
    except Exception as e:  # noqa: BLE001
        error_label.text = t("new_project.create_failed", error=str(e))
        return
    dialog.close()
    ui.navigate.reload()
