"""Project detail page. Displays full project info (R)."""

from nicegui import ui

from ...domain.models.project import Project
from ...infrastructure.bootstrap import get_current_user_repo
from .i18n import get_lang, t, toggle_lang
from .theme import logo

_CHEVRON_LEFT = (
    '<svg fill="currentColor" width="16" height="16" viewBox="0 0 20 20" '
    'xmlns="http://www.w3.org/2000/svg" aria-hidden="true" class="shrink-0">'
    '<path d="M12.4707 15.2792C12.7304 15.5389 12.7304 15.9609 12.4707 16.2206C12.211 16.4803 11.789 16.4803 11.5293 16.2206L5.7793 10.4706L5.69434 10.3661C5.52383 10.108 5.55103 9.75655 5.7793 9.52929L11.5293 3.77929L11.6338 3.69433C11.8919 3.52482 12.2434 3.55202 12.4707 3.77929C12.698 4.00656 12.7282 4.35807 12.5577 4.6162L12.4727 4.7207L7.19141 10L12.4707 15.2792Z"></path></svg>'  # noqa: E501
)

_SUN_ICON = (
    '<svg fill="currentColor" width="16" height="16" viewBox="0 0 20 20" '
    'xmlns="http://www.w3.org/2000/svg" aria-hidden="true" class="shrink-0">'
    '<path d="M10 3.5C10.3452 3.5 10.625 3.77982 10.625 4.125V5.375C10.625 5.72018 10.3452 6 10 6C9.65482 6 9.375 5.72018 9.375 5.375V4.125C9.375 3.77982 9.65482 3.5 10 3.5ZM10 14C10.3452 14 10.625 14.2798 10.625 14.625V15.875C10.625 16.2202 10.3452 16.5 10 16.5C9.65482 16.5 9.375 16.2202 9.375 15.875V14.625C9.375 14.2798 9.65482 14 10 14ZM10 7C8.34315 7 7 8.34315 7 10C7 11.6569 8.34315 13 10 13C11.6569 13 13 11.6569 13 10C13 8.34315 11.6569 7 10 7ZM4.125 10.625C3.77982 10.625 3.5 10.3452 3.5 10C3.5 9.65482 3.77982 9.375 4.125 9.375H5.375C5.72018 9.375 6 9.65482 6 10C6 10.3452 5.72018 10.625 5.375 10.625H4.125ZM14.625 10.625C14.2798 10.625 14 10.3452 14 10C14 9.65482 14.2798 9.375 14.625 9.375H15.875C16.2202 9.375 16.5 9.65482 16.5 10C16.5 10.3452 16.2202 10.625 15.875 10.625H14.625ZM5.75736 5.75736C6.00144 5.51328 6.00144 5.11655 5.75736 4.87247C5.51328 4.62839 5.11655 4.62839 4.87247 4.87247L3.98871 5.75623C3.74463 6.00031 3.74463 6.39704 3.98871 6.64112C4.23279 6.8852 4.62952 6.8852 4.8736 6.64112L5.75736 5.75736ZM15.1275 13.3589C15.3716 13.1148 15.7683 13.1148 16.0124 13.3589L16.8962 14.2426C17.1403 14.4867 17.1403 14.8834 16.8962 15.1275C16.6521 15.3716 16.2554 15.3716 16.0113 15.1275L15.1275 14.2438C14.8834 13.9997 14.8834 13.603 15.1275 13.3589ZM14.2426 5.75736C14.4867 5.51328 14.8834 5.51328 15.1275 5.75736L16.0113 6.64112C16.2554 6.8852 16.2554 7.28193 16.0113 7.52601C15.7672 7.77009 15.3705 7.77009 15.1264 7.52601L14.2426 6.64225C13.9985 6.39817 13.9985 6.00144 14.2426 5.75736ZM4.87247 15.1275C4.62839 14.8835 4.62839 14.4867 4.87247 14.2426L5.75623 13.3589C6.00031 13.1148 6.39704 13.1148 6.64112 13.3589C6.8852 13.603 6.8852 13.9997 6.64112 14.2438L5.75736 15.1275C5.51328 15.3716 5.11655 15.3716 4.87247 15.1275Z"></path></svg>'  # noqa: E501
)

_MOON_ICON = (
    '<svg fill="currentColor" width="16" height="16" viewBox="0 0 20 20" '
    'xmlns="http://www.w3.org/2000/svg" aria-hidden="true" class="shrink-0">'
    '<path d="M16.3589 13.1055C15.941 14.257 15.2225 15.2741 14.283 16.044C13.3436 16.814 12.2194 17.309 11.0068 17.475C9.79422 17.641 8.54114 17.4715 7.39942 16.9851C6.2577 16.4986 5.27144 15.7131 4.54975 14.7135C3.82806 13.7139 3.39793 12.5378 3.30399 11.3111C3.21004 10.0845 3.45572 8.85373 4.01463 7.75141C4.57355 6.64909 5.42482 5.71714 6.48069 5.05547C7.53657 4.3938 8.75782 4.02693 10.0105 3.99348C10.3141 3.98614 10.618 4.02782 10.9122 4.11776C10.3708 4.99472 10.0872 6.00763 10.0938 7.04024C10.1004 8.07285 10.397 9.08236 10.9498 9.95296C11.5026 10.8236 12.2891 11.5201 13.22 11.9648C14.151 12.4095 15.189 12.5844 16.2136 12.4694C16.3198 12.4574 16.425 12.439 16.5288 12.4143C16.4749 12.6478 16.406 12.8772 16.3224 13.1013L16.3589 13.1055Z"></path></svg>'  # noqa: E501
)

@ui.page("/project/{project_id}", title="Thesis Studio")
def project_page(project_id: str) -> None:
    """Redirect to EXPLORING phase."""
    ui.navigate.to(f"/project/{project_id}/exploring")

async def _build_header(project_id: str) -> None:
    project = await get_current_user_repo().get(project_id)
    if project is None:
        with ui.element("div").classes("flex items-center justify-center h-full"):
            ui.label("Project not found").classes("ts-text-secondary text-lg")
        return

    with ui.element("div").classes("flex h-full min-h-0 w-full flex-col"):  # noqa: SIM117  # noqa: SIM117  # noqa: SIM117  # noqa: SIM117  # noqa: SIM117
        with ui.element("div").classes("min-h-0 flex-1"):
            with ui.element("div").classes("flex h-full w-full flex-col"):
                with ui.element("main").classes("ts-bg-app min-h-0 w-full flex-1"):
                    with ui.element("div").classes("w-full h-full ts-bg-app box-border"):
                        _build_navbar()
                        _build_content(project)

def _build_navbar() -> None:
    with ui.element("div").classes(
        "flex items-center justify-between px-5 py-3 border-b ts-border-divider"
    ):
        with ui.element("div").classes("flex items-center gap-3"):
            with ui.link(target="/").classes(
                "ts-btn-tertiary inline-flex items-center justify-center "
                "rounded-full cursor-pointer h-[38px] w-[38px]"
            ):
                ui.html(_CHEVRON_LEFT)
            logo()
        with ui.element("div").classes("flex items-center gap-2"):
            _theme_toggle_button()
            _language_switch_button()

def _build_content(project: Project) -> None:
    with ui.element("div").classes("max-w-3xl mx-auto px-6 py-8"):  # noqa: SIM117  # noqa: SIM117  # noqa: SIM117  # noqa: SIM117  # noqa: SIM117
        with ui.element("div").classes("ts-bg-sidepanel rounded-xl p-8"):
            ui.label(project.title).classes("text-2xl font-bold ts-text-nav mb-6")

            if project.research_question:
                with ui.element("div").classes("mb-5"):
                    ui.label(t("project.page.question")).classes("ts-dialog-label")
                    ui.label(project.research_question).classes("text-sm ts-text-secondary")

            if project.keywords:
                with ui.element("div").classes("mb-5"):
                    ui.label(t("project.page.keywords")).classes("ts-dialog-label")
                    with ui.element("div").classes("ts-kw-chips mt-1"):
                        for kw in project.keywords:
                            with ui.element("div").classes("ts-kw-chip"):
                                ui.label(kw)

            if project.description:
                with ui.element("div").classes("mb-5"):
                    ui.label(t("project.page.description")).classes("ts-dialog-label")
                    ui.label(project.description).classes(
                        "text-sm ts-text-secondary whitespace-pre-wrap"
                    )

            with ui.element("div").classes("flex gap-6 mt-8 pt-6 border-t ts-border-outline"):
                with ui.element("div"):
                    ui.label(t("project.page.created")).classes("ts-dialog-label")
                    ui.label(project.created_at.strftime("%Y-%m-%d %H:%M")).classes(
                        "text-xs ts-text-tertiary"
                    )
                with ui.element("div"):
                    ui.label(t("project.page.updated")).classes("ts-dialog-label")
                    ui.label(project.updated_at.strftime("%Y-%m-%d %H:%M")).classes(
                        "text-xs ts-text-tertiary"
                    )

def _theme_toggle_button() -> None:
    with (
        ui.element("button")
        .classes(
            "ts-btn-tertiary inline-flex items-center justify-center "
            "rounded-full cursor-pointer h-[38px] w-[38px] px-0 gap-0"
        )
        .props("id=ts-theme-toggle")
    ):
        with ui.element("span").props("id=ts-icon-sun"):
            ui.html(_SUN_ICON)
        with ui.element("span").props("id=ts-icon-moon").style("display:none"):
            ui.html(_MOON_ICON)

def _language_switch_button() -> None:
    lang = get_lang()
    label = "\u4e2d" if lang == "zh" else "EN"
    btn = ui.element("button").classes(
        "ts-btn-tertiary inline-flex items-center justify-center "
        "rounded-full cursor-pointer h-[38px] px-3 text-sm font-medium"
    )

    def _switch(_: object) -> None:
        toggle_lang()
        ui.navigate.reload()

    btn.on("click", _switch)
    with btn:
        ui.label(label).classes("ts-lang-label")
