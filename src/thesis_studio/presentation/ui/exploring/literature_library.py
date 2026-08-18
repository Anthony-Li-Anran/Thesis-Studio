"""??????? ? ???????????????????"""

from __future__ import annotations

from nicegui import ui

from ..i18n import t


class LiteratureLibrary:
    """?????????????????????????"""

    def __init__(self, papers: list[dict] | None = None) -> None:
        self._papers: list[dict] = papers or []
        self._filtered: list[dict] = []
        self._search_text = ""
        self._sort_by = "title"
        self._container: ui.element | None = None

    def _apply_filter(self) -> None:
        """????????"""
        papers = self._papers
        if self._search_text:
            q = self._search_text.lower()
            papers = [
                p for p in papers
                if q in (p.get("title", "") or "").lower()
                or any(q in (a.get("name", "") if isinstance(a, dict) else str(a)).lower() for a in p.get("authors", []))
                or q in (p.get("abstract", "") or "").lower()
            ]
        if self._sort_by == "year":
            papers = sorted(papers, key=lambda p: p.get("year") or 0, reverse=True)
        elif self._sort_by == "citations":
            papers = sorted(papers, key=lambda p: p.get("citationCount", 0), reverse=True)
        else:
            papers = sorted(papers, key=lambda p: (p.get("title", "") or "").lower())
        self._filtered = papers
        self._refresh_display()

    def _refresh_display(self) -> None:
        if self._container is None:
            return
        self._container.clear()
        with self._container:
            self._render_list()

    def _render_list(self) -> None:
        if not self._filtered:
            with ui.element("div").classes(
                "flex flex-col items-center justify-center py-16 gap-3"
            ):
                ui.label(t("exploring.library")).classes("text-lg ts-text-secondary")
                ui.label(t("exploring.library_empty")).classes("text-sm ts-text-muted")
            return

        with ui.element("div").classes("flex flex-col gap-1"):
            for paper in self._filtered:
                self._render_paper_card(paper)

    def _render_paper_card(self, paper: dict) -> None:
        with ui.element("div").classes("p-4 rounded-xl ts-bg-card transition-colors"):
            with ui.element("div").classes("flex items-start justify-between gap-3"):
                with ui.element("div").classes("flex-1 min-w-0"):
                    ui.label(paper.get("title", "") or "Untitled").classes("text-sm font-semibold leading-snug")
                    authors_list = paper.get("authors", [])
                    if isinstance(authors_list, list):
                        author_names = [
                            a.get("name", "") if isinstance(a, dict) else str(a)
                            for a in authors_list
                        ]
                    else:
                        author_names = []
                    authors = ", ".join(author_names[:3])
                    if len(author_names) > 3:
                        authors += " et al."
                    meta = []
                    year = paper.get("year")
                    if year:
                        meta.append(str(year))
                    source = paper.get("source", "")
                    if source:
                        meta.append(source)
                    citations = paper.get("citationCount", 0)
                    if citations:
                        meta.append(f"{citations} citations")
                    ui.label(
                        f"{authors}  |  {'  |  '.join(meta)}"
                    ).classes("text-xs ts-text-muted mt-1")
                    abstract = paper.get("abstract", "") or ""
                    if abstract:
                        ui.label(abstract[:200]).classes(
                            "text-xs ts-text-secondary mt-1.5 leading-relaxed"
                        )
                with ui.element("div").classes("flex items-center gap-1 shrink-0"):
                    url = paper.get("url", "")
                    if url:
                        ui.link("", url, new_tab=True).classes("text-xs")

    async def build(self) -> ui.dialog:
        dlg = ui.dialog().props("maximized")

        with dlg, ui.card().classes("w-full h-full flex flex-col"):
            with ui.card_section().classes(
                "flex items-center justify-between px-6 py-4 border-b ts-border-divider"
            ):
                with ui.element("div").classes("flex items-center gap-4"):
                    count = len(self._filtered) if self._filtered else len(self._papers)
                    ui.label(t("exploring.library")).classes("text-lg font-semibold")
                    count_label = ui.label(f"{count} papers").classes("text-sm ts-text-muted")

                with ui.element("div").classes("flex items-center gap-3"):
                    search = ui.input(
                        placeholder=t("exploring.library_search")
                    ).props("outlined dense").classes("w-64")
                    search.on(
                        "update:model-value",
                        lambda e: self._on_search(e.args),
                    )
                    sort_options = {
                        "title": t("exploring.library_sort_title"),
                        "year": t("exploring.library_sort_year"),
                        "citations": t("exploring.library_sort_citations"),
                    }
                    sort = ui.select(
                        options=sort_options, value=self._sort_by
                    ).props("outlined dense").classes("w-28")
                    sort.on(
                        "update:model-value",
                        lambda e: self._on_sort(e.args),
                    )
                    ui.button(icon="close", on_click=lambda: dlg.close()).props("flat round")

            with ui.card_section().classes("flex-1 overflow-auto px-6 py-4"):
                self._container = ui.element("div")
                self._apply_filter()

        return dlg

    def _on_search(self, args: object) -> None:
        value = args.get("value", "") if isinstance(args, dict) else str(args)
        if isinstance(value, str):
            self._search_text = value
        self._apply_filter()

    def _on_sort(self, args: object) -> None:
        value = args.get("value", "") if isinstance(args, dict) else str(args)
        if isinstance(value, str) and value:
            self._sort_by = value
        self._apply_filter()
