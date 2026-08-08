"""??????????????????????"""

from collections.abc import Callable
from nicegui import ui

from ...infrastructure.bootstrap import get_current_user_repo
from .i18n import t

_CLOSE_ICON = (
    '<svg fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" '
    'width="18" height="18" xmlns="http://www.w3.org/2000/svg">'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>'
)


def delete_confirm_card(
    project_id: str, project_title: str, on_deleted: Callable[[], None] | None = None
) -> ui.dialog:
    with ui.dialog() as dialog:
        with ui.element("div").classes("ts-dialog-card").style("width:440px;max-width:92vw"):
            with ui.element("div").classes("ts-dialog-body relative"):
                _close_button(dialog)
                with ui.element("div").classes("ts-dialog-header"):
                    ui.label(t("delete_confirm.title")).classes("ts-dialog-title")
                ui.label(
                    t("delete_confirm.message") + " \u201c" + project_title + "\u201d?"
                ).classes("text-sm ts-text-secondary mt-2")
                ui.label(t("delete_confirm.warning")).classes("text-xs ts-text-tertiary mt-2")
                error_label = ui.label("").classes("ts-dialog-error")

                async def _do_delete() -> None:
                    await _on_delete(project_id, dialog, error_label, on_deleted)

                with ui.element("div").classes("ts-dialog-footer"):
                    ui.button(t("delete_confirm.cancel")).classes("ts-btn-secondary").props(
                        "unelevated no-caps"
                    ).on("click", dialog.close)
                    ui.button(t("delete_confirm.delete")).classes("ts-btn-primary").props(
                        "unelevated no-caps"
                    ).style("background-color: #dc2626 !important; border-color: #dc2626 !important").on(
                        "click", _do_delete
                    )
    return dialog


def _close_button(dialog: ui.dialog) -> None:
    btn = ui.element("div").classes("ts-dialog-close")
    btn.on("click", dialog.close)
    with btn:
        ui.html(_CLOSE_ICON)


async def _on_delete(
    project_id: str, dialog: ui.dialog, error_label: ui.label,
    on_deleted: Callable[[], None] | None,
) -> None:
    try:
        await get_current_user_repo().delete(project_id)
    except Exception as e:
        error_label.text = t("new_project.create_failed", error=str(e))
        return
    dialog.close()
    ui.notify(t("delete_confirm.deleted"), type="positive", position="top")
    if on_deleted:
        on_deleted()
