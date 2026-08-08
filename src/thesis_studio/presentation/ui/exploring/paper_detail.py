"""Slide-out paper detail panel."""

from nicegui import ui


class PaperDetail:
    """Slide-out panel showing paper details."""

    def __init__(self) -> None:
        self._panel: ui.element | None = None
        self._visible = False

    def build(self) -> None:
        """Render the detail panel container (initially hidden)."""
        self._panel = (
            ui.element("div")
            .classes("fixed right-0 top-0 h-full w-[360px] ts-bg-sidepanel z-50")
            .style("transform:translateX(100%);transition:transform 0.25s ease;border-radius:16px 0 0 16px;box-shadow:-4px 0 24px rgba(0,0,0,0.4)")  # noqa: E501
        )

    def show(self, paper: dict[str, str]) -> None:
        """Show paper details in the panel."""
        if self._panel is None:
            return
        self._panel.clear()
        with self._panel:
            _render_paper_content(paper)
        self._panel.style("transform:translateX(0)")
        self._visible = True

    def hide(self) -> None:
        """Hide the panel."""
        if self._panel is None:
            return
        self._panel.style("transform:translateX(100%)")
        self._visible = False


def _render_paper_content(paper: dict[str, str]) -> None:
    """Render paper details inside the panel."""
    with ui.element("div").classes("p-6 h-full overflow-y-auto"):
        with ui.element("div").classes("flex justify-between items-start mb-4"):
            ui.label(paper.get("title", "")).classes("text-base font-bold ts-text-nav flex-1")
            close_btn = ui.element("button").classes("ts-btn-tertiary w-8 h-8 rounded-full flex items-center justify-center flex-none ml-2")  # noqa: E501
            with close_btn:
                ui.label("x").classes("text-sm")
        _meta_row("Authors", paper.get("authors", ""))
        _meta_row("Year", str(paper.get("year", "")))
        _meta_row("Source", paper.get("source", ""))
        _section("Abstract", paper.get("abstract", ""))
        _section("Method", paper.get("method", ""))
        _section("Conclusion", paper.get("conclusion", ""))
        if paper.get("relations"):
            _relations(paper["relations"])  # type: ignore[arg-type]


def _meta_row(label: str, value: str) -> None:
    if not value:
        return
    with ui.element("div").classes("flex gap-2 mb-2"):
        ui.label(label).classes("text-xs font-medium ts-text-nav-secondary w-16 flex-none")
        ui.label(value).classes("text-xs ts-text-nav")


def _section(title: str, content: str) -> None:
    if not content:
        return
    with ui.element("div").classes("mt-4"):
        ui.label(title).classes("text-xs font-semibold ts-text-nav-secondary mb-1")
        ui.label(content).classes("text-xs ts-text-nav-secondary leading-relaxed")


def _relations(rels: list[str]) -> None:
    with ui.element("div").classes("mt-4"):
        ui.label("Relations").classes("text-xs font-semibold ts-text-nav-secondary mb-1")
        with ui.element("div").classes("flex flex-wrap gap-1"):
            for r in rels:
                ui.label(r).classes(
                    "text-[10px] px-2 py-0.5 rounded-full"
                ).style("background:var(--button-secondary-bg);color:var(--button-secondary-text)")
