"""Markdown outline editor with three modes: edit, preview, split.
Uses NiceGUI ui.textarea with CSS overrides for proper scrolling.
"""

from __future__ import annotations

from collections.abc import Callable
from contextlib import suppress
from typing import Any

from nicegui import ui

from ..i18n import t as _t

_EDITOR_CSS = """<style>
.ts-outline-editor { display:flex;flex-direction:column;height:100%;min-height:0; }
.ts-outline-editor .mode-tabs { display:flex;gap:2px;background:var(--bg-sidepanel);border-radius:10px;padding:3px; }
.ts-outline-editor .mode-tab {
  padding:5px 14px;border-radius:8px;font-size:12px;font-weight:500;
  cursor:pointer;transition:all 0.2s;border:none;background:transparent;color:var(--fg-tertiary);
}
.ts-outline-editor .mode-tab.active {
  background:var(--bg-app);color:var(--text-nav-primary);box-shadow:0 1px 3px rgba(0,0,0,0.08);
}
.ts-outline-view { position:absolute;top:0;left:0;right:0;bottom:0;overflow:hidden; }
.ts-outline-view .q-field { height:100% !important; }
.ts-outline-view .q-field__control { height:100% !important; min-height:0 !important; }
.ts-outline-view .q-field__native { resize:none !important; }
.ts-outline-view textarea {
  font-family:"JetBrains Mono","Cascadia Code","Fira Code",monospace !important;
  font-size:13px !important;line-height:1.7 !important;tab-size:2;
  overflow-y:auto !important;
}
.ts-outline-edit textarea { padding:20px 24px !important;resize:none !important;font-size:13px !important;line-height:1.7 !important;overflow-y:auto !important; }
.ts-outline-split { display:flex;height:100%; }
.ts-outline-split-left { width:50%;height:100%;overflow:hidden; }
.ts-outline-split-right { width:50%;height:100%;overflow-y:auto;padding:24px 28px;font-size:14px;line-height:1.8; }
.ts-outline-split-right h1 { font-size:1.5rem;font-weight:700;margin:0 0 0.5em; }
.ts-outline-split-right h2 { font-size:1.2rem;font-weight:600;margin:1.2em 0 0.4em; }
.ts-outline-split-right h3 { font-size:1rem;font-weight:500;margin:1em 0 0.3em; }
.ts-outline-split-right p { margin:0.4em 0; }
.ts-outline-split-right ul,.ts-outline-split-right ol { margin:0.4em 0;padding-left:1.5em; }
.ts-outline-split-right li { margin:0.2em 0; }
.ts-outline-split .q-field { height:100% !important; }
.ts-outline-split .q-field__control { height:100% !important;min-height:0 !important; }
.ts-outline-split textarea { padding:16px 20px !important;font-size:13px !important;line-height:1.7 !important;overflow-y:auto !important;resize:none !important; }
.ts-outline-preview { position:absolute;top:0;left:0;right:0;bottom:0;overflow-y:auto;padding:24px 28px;font-size:14px;line-height:1.8; }
.ts-outline-preview h1 { font-size:1.5rem;font-weight:700;margin:0 0 0.5em; }
.ts-outline-preview h2 { font-size:1.2rem;font-weight:600;margin:1.2em 0 0.4em; }
.ts-outline-preview h3 { font-size:1rem;font-weight:500;margin:1em 0 0.3em; }
.ts-outline-preview p { margin:0.4em 0; }
.ts-outline-preview ul,.ts-outline-preview ol { margin:0.4em 0;padding-left:1.5em; }
.ts-outline-preview li { margin:0.2em 0; }

.ts-outline-preview pre, .ts-outline-split-right pre {
  background: rgba(0,0,0,0.2); border: 1px solid var(--border-outline);
  border-radius: 8px; padding: 12px 16px; overflow-x: auto;
  font-size: 0.85em; line-height: 1.5;
}
.ts-outline-preview pre code, .ts-outline-split-right pre code {
  background: none; padding: 0; font-family: "JetBrains Mono", monospace;
}
.ts-outline-preview blockquote, .ts-outline-split-right blockquote {
  border-left: 3px solid #7c3aed; padding: 6px 14px;
  background: rgba(124,58,237,0.06); border-radius: 0 8px 8px 0;
  margin: 0.5em 0; color: var(--text-nav-secondary);
}
.ts-outline-preview table, .ts-outline-split-right table {
  border-collapse: collapse; width: 100%; margin: 0.5em 0;
}
.ts-outline-preview th, .ts-outline-split-right th,
.ts-outline-preview td, .ts-outline-split-right td {
  border: 1px solid var(--border-outline); padding: 6px 12px; text-align: left;
}
.ts-outline-preview th, .ts-outline-split-right th {
  background: rgba(255,255,255,0.04); font-weight: 600;
}
</style>"""


class OutlineEditor:
    def __init__(self) -> None:
        self._content: str = ""
        self._mode: str = "edit"
        self._edit_container: ui.element | None = None
        self._preview_container: ui.element | None = None
        self._split_container: ui.element | None = None
        self._edit_area: ui.textarea | None = None
        self._split_edit_area: ui.textarea | None = None
        self._preview_html: ui.html | None = None
        self._split_preview_html: ui.html | None = None
        self._on_change: Callable[[str], None] | None = None
        self._tab_buttons: dict[str, ui.element] = {}

    @property
    def content(self) -> str:
        return self._content

    @content.setter
    def content(self, value: str) -> None:
        self._content = value
        with suppress(RuntimeError):
            self._sync_ui()

    def on_change(self, callback: Callable[[str], None]) -> None:
        self._on_change = callback

    def build(self) -> None:
        with (
            ui.element("div")
            .classes("ts-outline-editor")
            .style("display:flex;flex-direction:column;height:100%;min-height:0")
        ):
            ui.add_head_html(_EDITOR_CSS)
            self._build_toolbar()
            with ui.element("div").style("flex:1;min-height:0;position:relative"):
                self._build_edit_view()
                self._build_preview_view()
                self._build_split_view()
            self._update_visibility()

    def _build_toolbar(self) -> None:
        with ui.element("div").classes(
            "flex items-center justify-between px-4 py-3 border-b ts-border-divider"
        ):
            ui.label(_t("designing.outline_title")).classes("text-sm font-medium ts-text-nav")
            with ui.element("div").classes("mode-tabs"):
                for mode, label in [
                    ("edit", _t("designing.mode_edit")),
                    ("preview", _t("designing.mode_preview")),
                    ("split", _t("designing.mode_split")),
                ]:
                    tab = ui.element("button").classes("mode-tab")
                    if mode == self._mode:
                        tab.classes("active")
                    tab.on("click", lambda _m=mode: self._switch_mode(_m))
                    self._tab_buttons[mode] = tab
                    with tab:
                        ui.label(label)

    def _build_edit_view(self) -> None:
        self._edit_container = ui.element("div").classes("ts-outline-view ts-outline-edit")
        with self._edit_container:
            self._edit_area = ui.textarea(value=self._content).style("width:100%;height:100%")
            self._edit_area.on("update:model-value", self._handle_edit_change)

    def _build_preview_view(self) -> None:
        self._preview_container = (
            ui.element("div").classes("ts-outline-preview").style("display:none")
        )
        with self._preview_container:
            self._preview_html = ui.html(self._md_to_html(self._content))

    def _build_split_view(self) -> None:
        self._split_container = (
            ui.element("div").classes("ts-outline-split ts-outline-view").style("display:none")
        )
        with self._split_container:
            with ui.element("div").classes("ts-outline-split-left"):
                self._split_edit_area = ui.textarea(value=self._content).style(
                    "width:100%;height:100%"
                )
                self._split_edit_area.on("update:model-value", self._handle_split_edit)
            self._split_preview_html = ui.html(self._md_to_html(self._content)).classes(
                "ts-outline-split-right"
            )

    def _handle_edit_change(self, e: Any) -> None:
        val = str(e.args[0]) if e.args else ""
        self._content = val
        if self._on_change:
            self._on_change(val)

    def _handle_split_edit(self, e: Any) -> None:
        val = str(e.args[0]) if e.args else ""
        self._content = val
        if self._split_preview_html is not None:
            with suppress(RuntimeError):
                self._split_preview_html.set_content(self._md_to_html(val))
        if self._on_change:
            self._on_change(val)

    def _switch_mode(self, mode: str) -> None:
        if mode == self._mode:
            return
        if self._edit_area is not None and self._mode == "edit":
            self._content = self._edit_area.value or ""
        elif self._split_edit_area is not None and self._mode == "split":
            self._content = self._split_edit_area.value or ""

        self._mode = mode

        if mode == "preview" and self._preview_html is not None:
            with suppress(RuntimeError):
                self._preview_html.set_content(self._md_to_html(self._content))
        elif mode == "split" and self._split_preview_html is not None:
            with suppress(RuntimeError):
                self._split_preview_html.set_content(self._md_to_html(self._content))
                if self._split_edit_area is not None:
                    self._split_edit_area.value = self._content
        elif mode == "edit" and self._edit_area is not None:
            with suppress(RuntimeError):
                self._edit_area.value = self._content

        self._update_visibility()
        self._update_tab_buttons()

    def _update_visibility(self) -> None:
        if self._edit_container is not None:
            self._edit_container.style(f"display:{'block' if self._mode == 'edit' else 'none'}")
        if self._preview_container is not None:
            self._preview_container.style(
                f"display:{'block' if self._mode == 'preview' else 'none'}"
            )
        if self._split_container is not None:
            self._split_container.style(f"display:{'flex' if self._mode == 'split' else 'none'}")

    def _update_tab_buttons(self) -> None:
        for m, btn in self._tab_buttons.items():
            if m == self._mode:
                btn.classes("mode-tab active")
            else:
                btn.classes(remove="active")

    def _sync_ui(self) -> None:
        import logging

        _log = logging.getLogger(__name__)
        if self._edit_area is None and self._preview_html is None:
            return  # UI not yet built, skip silently
        html = self._md_to_html(self._content)
        try:
            if self._edit_area is not None:
                self._edit_area.value = self._content
        except RuntimeError as e:
            _log.debug("_sync_ui edit_area: %s", e)
        try:
            if self._preview_html is not None:
                self._preview_html.set_content(html)
        except RuntimeError as e:
            _log.debug("_sync_ui preview_html: %s", e)
        try:
            if self._split_edit_area is not None:
                self._split_edit_area.value = self._content
        except RuntimeError as e:
            _log.debug("_sync_ui split_edit: %s", e)
        try:
            if self._split_preview_html is not None:
                self._split_preview_html.set_content(html)
        except RuntimeError as e:
            _log.debug("_sync_ui split_preview: %s", e)

    @staticmethod
    def _md_to_html(md: str) -> str:
        if not md:
            return '<p style="color:var(--fg-tertiary);padding:24px 28px">No content</p>'
        try:
            import markdown2

            return markdown2.markdown(md, extras=["fenced-code-blocks", "tables", "code-friendly", "cuddled-lists", "header-ids", "strike", "target-blank-links", "task_list", "footnotes"])
        except ImportError:
            import re as _re

            result = []
            in_code = False
            for line in md.split("\n"):
                if line.strip().startswith("```"):
                    in_code = not in_code
                    tag = "<pre><code>" if in_code else "</code></pre>"
                    result.append(tag)
                    continue
                if in_code:
                    result.append(line)
                    continue
                # Bold and italic
                line = _re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line)
                line = _re.sub(r"\*(.+?)\*", r"<em>\1</em>", line)
                # Inline code
                line = _re.sub(r"`(.+?)`", r"<code>\1</code>", line)
                # Links
                line = _re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', line)
                if line.startswith("### "):
                    result.append(f"<h3>{line[4:]}</h3>")
                elif line.startswith("## "):
                    result.append(f"<h2>{line[3:]}</h2>")
                elif line.startswith("# "):
                    result.append(f"<h1>{line[2:]}</h1>")
                elif line.strip():
                    result.append(f"<p>{line}</p>")
                else:
                    result.append("<br>")
            return "\n".join(result)
