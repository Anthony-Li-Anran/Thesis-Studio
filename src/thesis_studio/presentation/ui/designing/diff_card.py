"""Diff suggestion card for DESIGNING chat.

AI proposes outline changes, user confirms or rejects.
"""

from __future__ import annotations

from collections.abc import Callable

from nicegui import ui

from ..i18n import t as _t


class DiffCard:
    """Diff suggestion card for DESIGNING chat.

    AI proposes outline changes, user confirms or rejects.
    """

    def __init__(self) -> None:
        self._suggestions: list[dict[str, str]] = []
        self._handled: set[int] = set()
        self._card_container: ui.element | None = None
        self._on_confirm: Callable[[list[dict[str, str]]], None] | None = None
        self._on_reject: Callable[[], None] | None = None

    @property
    def suggestions(self) -> list[dict[str, str]]:
        return self._suggestions

    @suggestions.setter
    def suggestions(self, value: list[dict[str, str]]) -> None:
        self._suggestions = value
        self._handled.clear()

    def on_confirm(self, callback: Callable[[list[dict[str, str]]], None]) -> None:
        self._on_confirm = callback

    def on_reject(self, callback: Callable[[], None]) -> None:
        self._on_reject = callback

    def build(self) -> None:
        if not self._suggestions:
            return
        self._card_container = ui.element("div").classes(
            "ts-bg-sidepanel rounded-xl border border-purple-500/30 overflow-hidden"
        )
        with self._card_container:
            self._render_content()

    def _render_content(self) -> None:
        unhandled = [(i, s) for i, s in enumerate(self._suggestions) if i not in self._handled]
        if not unhandled:
            self._dismiss()
            return
        with (
            ui.element("div")
            .classes("flex items-center justify-between px-4 py-2.5 border-b ts-border-divider")
            .style("background:rgba(124,58,237,0.08)")
        ):
            with ui.element("div").classes("flex items-center gap-2"):
                ui.label("\U0001f504").classes("text-sm")
                ui.label(_t("designing.diff_title")).classes("text-sm font-medium ts-text-nav")
            ui.label(f"{len(unhandled)} {_t('designing.diff_count')}").classes(
                "text-xs ts-text-tertiary"
            )
        for i, s in unhandled:
            self._render_suggestion(i, s)
        if len(unhandled) > 1:
            with ui.element("div").classes("flex gap-2 px-4 py-2.5 border-t ts-border-divider"):
                ui.button(
                    _t("designing.diff_accept_all"), on_click=self._handle_confirm_all
                ).classes("ts-btn-primary text-xs").props("no-caps dense")
                ui.button(
                    _t("designing.diff_reject_all"), on_click=self._handle_reject_all
                ).classes("ts-btn-secondary text-xs").props("no-caps dense")

    def _render_suggestion(self, index: int, suggestion: dict[str, str]) -> None:
        section = suggestion.get("section", "")
        old_text = suggestion.get("old", "")
        new_text = suggestion.get("new", "")

        with ui.element("div").classes("px-4 py-3 border-b ts-border-divider last:border-b-0"):
            if section:
                ui.label(f"{_t('designing.diff_section')}: {section}").classes(
                    "text-xs font-medium ts-text-tertiary mb-2"
                )

            if old_text:
                with ui.element("div").classes("mb-1.5"):
                    ui.label(_t("designing.diff_old")).classes("text-[10px] text-red-400 mb-0.5")
                    with (
                        ui.element("div")
                        .classes("rounded-lg px-3 py-2 text-xs")
                        .style("background:rgba(239,68,68,0.08);color:var(--text-nav-secondary)")
                    ):
                        ui.label(old_text).classes("text-xs")

            if new_text:
                with ui.element("div").classes("mb-2"):
                    ui.label(_t("designing.diff_new")).classes("text-[10px] text-green-400 mb-0.5")
                    with (
                        ui.element("div")
                        .classes("rounded-lg px-3 py-2 text-xs")
                        .style("background:rgba(34,197,94,0.08);color:var(--text-nav-primary)")
                    ):
                        ui.label(new_text).classes("text-xs")

            with ui.element("div").classes("flex gap-2"):
                ui.button(
                    _t("designing.diff_confirm"),
                    on_click=lambda i=index: self._handle_confirm_one(i),
                ).classes("text-xs").props("no-caps dense flat").style("color:#22c55e")
                ui.button(
                    _t("designing.diff_modify"), on_click=lambda i=index: self._handle_modify_one(i)
                ).classes("text-xs").props("no-caps dense flat").style("color:#f59e0b")
                ui.button(
                    _t("designing.diff_reject"), on_click=lambda i=index: self._handle_reject_one(i)
                ).classes("text-xs").props("no-caps dense flat").style("color:#ef4444")

    def _handle_confirm_one(self, index: int) -> None:
        if index in self._handled:
            return
        self._handled.add(index)
        if self._on_confirm:
            self._on_confirm([self._suggestions[index]])
        self._refresh()

    def _handle_confirm_all(self) -> None:
        for i in range(len(self._suggestions)):
            self._handled.add(i)
        if self._on_confirm:
            self._on_confirm(list(self._suggestions))
        self._dismiss()

    def _handle_reject_one(self, index: int) -> None:
        if index in self._handled:
            return
        self._handled.add(index)
        self._refresh()

    def _handle_reject_all(self) -> None:
        for i in range(len(self._suggestions)):
            self._handled.add(i)
        self._dismiss()

    def _handle_modify_one(self, index: int) -> None:
        if index in self._handled:
            return
        s = self._suggestions[index]
        with ui.dialog() as dlg, ui.card().classes("w-full max-w-lg"):
            with ui.card_section().classes("flex items-center justify-between"):
                ui.label(_t("designing.diff_modify_title")).classes("text-base font-bold")
                ui.button(icon="close", on_click=lambda: dlg.close()).props("flat round")
            with ui.card_section():
                ta = (
                    ui.textarea(
                        value=s.get("new", ""),
                        placeholder=_t("designing.diff_modify_hint"),
                    )
                    .classes("w-full")
                    .style("min-height:100px")
                    .props("autogrow")
                )
            with ui.card_section().classes("flex justify-end gap-2"):
                ui.button(_t("designing.cancel"), on_click=lambda: dlg.close()).props("flat")

                def _apply_and_close(idx: int = index) -> None:
                    self._apply_modify(idx, ta.value)
                    dlg.close()

                ui.button(
                    _t("designing.apply"),
                    on_click=_apply_and_close,
                ).props("flat")
        dlg.open()

    def _apply_modify(self, index: int, new_text: str) -> None:
        self._suggestions[index]["new"] = new_text
        self._handled.add(index)
        if self._on_confirm:
            self._on_confirm([self._suggestions[index]])
        self._refresh()

    def _refresh(self) -> None:
        if self._card_container is None:
            return
        self._card_container.clear()
        with self._card_container:
            self._render_content()

    def _dismiss(self) -> None:
        if self._card_container is not None:
            self._card_container.clear()
            self._card_container.delete()
            self._card_container = None
        if self._on_reject:
            self._on_reject()
