"""?????????? new_project_card ???????????"""

from collections.abc import Callable
from nicegui import ui

from ...domain.models.project import Project
from ...infrastructure.bootstrap import get_current_user_repo
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


def edit_project_card(project: Project, on_saved: Callable[[], None] | None = None) -> ui.dialog:
    state: dict = {"keywords": list(project.keywords)}

    with ui.dialog() as dialog:
        with ui.element("div").classes("ts-dialog-card").style("width:600px;max-width:92vw"):
            with ui.element("div").classes("ts-dialog-body relative"):
                _close_button(dialog)
                with ui.element("div").classes("ts-dialog-header"):
                    ui.label(t("edit_project.title")).classes("ts-dialog-title")
                with ui.element("div").classes("ts-dialog-form"):
                    fields = _form(state, project)
                error_label = ui.label("").classes("ts-dialog-error")

                async def _save() -> None:
                    await _on_save(state, dialog, fields, error_label, project, on_saved)

                _footer(dialog, _save)
    return dialog


def _close_button(dialog: ui.dialog) -> None:
    btn = ui.element("div").classes("ts-dialog-close")
    btn.on("click", dialog.close)
    with btn:
        ui.html(_CLOSE_ICON)


def _form(state: dict, project: Project) -> dict:
    title = _field(t("new_project.field.title"), t("new_project.ph.title"), project.title)
    question = _field(
        t("new_project.field.question"), t("new_project.ph.question"),
        project.research_question, textarea=True
    )
    _keyword_field(state)
    description = _field(
        t("new_project.field.description"), t("new_project.ph.description"),
        project.description, textarea=True
    )
    return {"title": title, "question": question, "description": description}


def _field(label: str, placeholder: str, value: str = "", textarea: bool = False) -> ui.input:
    with ui.element("div").classes("ts-dialog-field"):
        ui.label(label).classes("ts-dialog-label")
        cls = "ts-dialog-input ts-dialog-textarea w-full" if textarea else "ts-dialog-input w-full"
        widget = (
            ui.textarea(placeholder=placeholder, value=value)
            if textarea
            else ui.input(placeholder=placeholder, value=value)
        )
        return widget.classes(cls).props("dark dense")


def _keyword_field(state: dict) -> None:
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
    with ui.element("div").classes("ts-kw-chip"):
        ui.label(kw)
        btn = ui.element("button").classes("ts-kw-chip-x")

        def _remove(_: object) -> None:
            state["keywords"].remove(kw)
            on_change()

        btn.on("click", _remove)
        with btn:
            ui.html(_X_ICON)


def _footer(dialog: ui.dialog, on_save) -> None:
    with ui.element("div").classes("ts-dialog-footer"):
        ui.button(t("new_project.cancel")).classes("ts-btn-secondary").props(
            "unelevated no-caps"
        ).on("click", dialog.close)
        ui.button(t("edit_project.save")).classes("ts-btn-primary").props(
            "unelevated no-caps"
        ).on("click", on_save)


async def _on_save(
    state: dict, dialog: ui.dialog, fields: dict, error_label: ui.label,
    project: Project, on_saved: Callable[[], None] | None,
) -> None:
    title = fields["title"].value.strip()
    if not title:
        error_label.text = t("new_project.title_required")
        return
    project.title = title
    project.research_question = fields["question"].value.strip()
    project.description = fields["description"].value.strip()
    project.keywords = list(state["keywords"])
    try:
        await get_current_user_repo().update(project)
    except Exception as e:
        error_label.text = t("new_project.create_failed", error=str(e))
        return
    dialog.close()
    ui.notify(t("edit_project.saved"), type="positive", position="top")
    if on_saved:
        on_saved()
