"""Three-dot settings dropdown per project row: Edit / Delete."""

from nicegui import ui
from .i18n import t

_THREE_DOTS = (
    '<svg fill="currentColor" width="16" height="16" viewBox="0 0 20 20" '
    'xmlns="http://www.w3.org/2000/svg" aria-hidden="true" class="shrink-0">'
    '<path d="M6 10a2 2 0 11-4 0 2 2 0 014 0zM12 10a2 2 0 11-4 0 2 2 0 014 0zM16'
    ' 12a2 2 0 100-4 2 2 0 000 4z"></path></svg>'
)


def project_menu(on_edit, on_delete):
    state = {"open": False}

    with ui.element("div").classes("relative flex-none") as container:
        trigger = ui.element("button").classes(
            "ts-btn-tertiary inline-flex items-center justify-center "
            "rounded-full cursor-pointer w-[26px] h-[26px] "
            "hover:ts-text-nav transition-colors"
        )
        with trigger:
            ui.html(_THREE_DOTS)

        dropdown = ui.element("div").classes(
            "absolute right-0 top-full mt-1 z-50 "
            "ts-bg-sidepanel border ts-border-outline rounded-xl "
            "shadow-lg py-1 min-w-[140px]"
        ).style("display:none")

        def toggle():
            state["open"] = not state["open"]
            dropdown.style("display:" + ("block" if state["open"] else "none"))

        trigger.on("click", toggle)

        with dropdown:
            btn_edit = ui.element("button").classes(
                "w-full text-left px-4 py-2 text-sm transition-colors "
                "ts-text-nav-secondary hover:ts-text-nav"
            )
            btn_edit.on("click", lambda: (toggle(), on_edit()))
            with btn_edit:
                ui.label(t("project.edit"))

            btn_del = ui.element("button").classes(
                "w-full text-left px-4 py-2 text-sm transition-colors"
            ).style("color: #ef4444")
            btn_del.on("click", lambda: (toggle(), on_delete()))
            with btn_del:
                ui.label(t("project.delete"))

    return container
