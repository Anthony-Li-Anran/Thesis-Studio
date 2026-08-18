"""Checklist component for DESIGNING phase - tracks section completion status."""

from __future__ import annotations

from collections.abc import Callable
from contextlib import suppress

from nicegui import ui

from ..i18n import t as _t


class Checklist:
    """Compact checklist bar showing section completion status at the top of the outline editor."""

    def __init__(self, sections: list[str] | None = None) -> None:
        self._sections: list[str] = sections or [
            "title", "introduction", "literature_review",
            "research_design", "expected_results", "discussion", "conclusion",
        ]
        self._status: dict[str, bool] = {}
        self._container: ui.element | None = None
        self._on_change: Callable[[str, bool], None] | None = None

    @property
    def all_completed(self) -> bool:
        return all(self._status.get(s, False) for s in self._sections)

    def on_change(self, callback: Callable[[str, bool], None]) -> None:
        self._on_change = callback

    def set_status(self, section: str, completed: bool) -> None:
        self._status[section] = completed
        with suppress(RuntimeError):
            self._render()

    def set_all_status(self, status: dict[str, bool]) -> None:
        self._status.update(status)
        with suppress(RuntimeError):
            self._render()

    def build(self) -> None:
        self._container = ui.element("div").classes("w-full")
        self._render()

    def _render(self) -> None:
        if self._container is None:
            return
        with suppress(RuntimeError):
            self._container.clear()
            with self._container:
                with ui.element("div").classes(
                    "flex items-center gap-1.5 px-4 py-2 border-b ts-border-divider"
                ):
                    ui.label(_t("designing.checklist")).classes(
                        "text-[11px] font-medium ts-text-tertiary mr-2 whitespace-nowrap"
                    )
                    for s in self._sections:
                        done = self._status.get(s, False)
                        label = _t(f"designing.section_{s}")
                        chip_cls = (
                            "text-[11px] px-2.5 py-1 rounded-full whitespace-nowrap "
                            "transition-colors cursor-pointer"
                        )
                        if done:
                            chip_cls += " ts-text-nav"
                            style = "background:rgba(22,163,74,0.15);color:#16a34a"
                        else:
                            chip_cls += " ts-text-tertiary"
                            style = "background:var(--bg-sidepanel)"
                        chip = ui.element("button").classes(chip_cls).style(style)
                        chip.on("click", lambda _s=s, _d=done: self._toggle(_s, _d))
                        with chip:
                            icon = "✓" if done else "○"
                            ui.label(f"{icon} {label}").classes("text-[11px]")

    def _toggle(self, section: str, current: bool) -> None:
        new_status = not current
        self._status[section] = new_status
        self._render()
        if self._on_change:
            self._on_change(section, new_status)

    def auto_detect(self, markdown_content: str) -> dict[str, bool]:
        """Auto-detect section completion from markdown content."""
        status: dict[str, bool] = {}
        for s in self._sections:
            key = _t(f"designing.section_{s}")
            # Check if the section heading exists and has content after it
            found = False
            for line in markdown_content.splitlines():
                if line.strip().startswith("###") and key.lower() in line.lower():
                    found = True
                    break
            if not found:
                for line in markdown_content.splitlines():
                    if line.strip().startswith("##") and key.lower() in line.lower():
                        found = True
                        break
            status[s] = found
        return status
