"""Multi-agent chat panel with @mention, diff suggestions, and reviewed debate."""

from __future__ import annotations

import asyncio
import os
from contextlib import suppress
from typing import Any

from nicegui import ui

from ..i18n import t as _t
from .chat_renderer import AGENT_LABELS, render_message
from .debate_orchestrator import ChatState, DebateOrchestrator
from .diff_card import DiffCard

_AT_MENU_CSS = """<style>
#ts-at-menu{position:fixed;z-index:99999;width:170px;background:var(--bg-sidepanel);
  border:1px solid var(--border-outline);border-radius:10px;
  box-shadow:0 8px 24px rgba(0,0,0,0.3);overflow:hidden;display:none;}
#ts-at-menu .ts-at-item{display:flex;align-items:center;gap:8px;padding:8px 14px;
  cursor:pointer;font-size:13px;color:var(--text-nav-primary);transition:background 0.1s;}
#ts-at-menu .ts-at-item:hover{background:var(--nav-bg-hover-strong);}
#ts-at-menu .ts-at-divider{height:1px;background:var(--border-outline);margin:2px 0;}
#ts-at-menu .ts-at-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0;}
</style>"""

_AT_JS_PATH = os.path.join(os.path.dirname(__file__), "at_mention.js")


def _load_at_mention_js() -> str:
    with open(_AT_JS_PATH, encoding="utf-8") as f:
        return f.read()


class DesigningChatRoom:
    """Chat room component: handles UI rendering, delegates logic to DebateOrchestrator."""

    def __init__(self, outline_editor: Any) -> None:
        self._outline_editor = outline_editor
        self._msgs: list[dict[str, str]] = []
        self._container: ui.element | None = None
        self._input: ui.input | None = None
        self._orchestrator = DebateOrchestrator(
            outline_getter=lambda: self._outline_editor.content if self._outline_editor else "",
            max_rounds=3,
        )
        self._wire_orchestrator()

    def _wire_orchestrator(self) -> None:
        self._orchestrator.on_add_message(self._add_message)
        self._orchestrator.on_add_system(self._add_system)
        self._orchestrator.on_replace_last(self._replace_last)
        self._orchestrator.on_suggestions(self._on_suggestions_received)

    def build(self) -> None:
        with ui.element("div").style("display:flex;flex-direction:column;height:100%;min-height:0"):
            ui.add_head_html(_AT_MENU_CSS)
            self._build_header()
            self._container = (
                ui.element("div")
                .classes("flex-1 overflow-y-auto px-4 py-4 space-y-3")
                .style("min-height:0")
            )
            self._build_input()
            ui.timer(0.5, lambda: self._init_at_mention(), once=True)

    def _init_at_mention(self) -> None:
        ui.run_javascript(_load_at_mention_js())

    def _build_header(self) -> None:
        with ui.element("div").classes("px-4 py-3 border-b ts-border-divider"):
            ui.label(_t("designing.title")).classes("text-sm font-medium ts-text-nav")

    def _build_input(self) -> None:
        with ui.element("div").classes(
            "flex items-center gap-2 px-4 py-3 border-t ts-border-divider"
        ):
            self._input = (
                ui.input(placeholder=_t("designing.input_placeholder"))
                .classes("ts-dialog-input flex-1")
                .props("dark dense")
            )
            self._input.on("keydown.enter", lambda e: asyncio.ensure_future(self._on_send()))
            send_btn = ui.element("button").classes(
                "ts-btn-tertiary inline-flex items-center justify-center"
                " rounded-full h-[38px] w-[38px] flex-none"
            )
            send_btn.on("click", lambda e: asyncio.ensure_future(self._on_send()))
            with send_btn:
                ui.html(
                    '<svg fill="none" viewBox="0 0 24 24" stroke-width="2"'
                    ' stroke="currentColor" width="18" height="18">'
                    '<path stroke-linecap="round" stroke-linejoin="round"'
                    ' d="M4.5 10.5L12 3m0 0l7.5 7.5M12 3v18"/></svg>'
                )

    async def _on_send(self) -> None:
        if not self._input:
            return
        pending_text = (self._input.value or "").strip()
        state = self._orchestrator.state
        if state != ChatState.IDLE:
            if pending_text:
                self._orchestrator.queue_message(pending_text)
                self._add_system("消息已排队，当前响应完成后自动处理...")
                self._input.value = ""
                return
            self._orchestrator.request_stop()
            self._add_system("已请求停止...")
            self._input.value = ""
            return
        if not pending_text:
            return
        self._input.value = ""
        self._add_message("user", pending_text, "")
        await self._orchestrator.handle_user_input(pending_text)
        self._process_pending()

    def _add_message(self, role: str, content: str, agent: str = "") -> None:
        self._msgs.append({"role": role, "content": content, "agent": agent})
        self._render_all()

    def _add_system(self, content: str) -> None:
        self._msgs.append({"role": "system", "content": content, "agent": ""})
        self._render_all()

    def _render_all(self) -> None:
        if self._container is None:
            return
        with suppress(RuntimeError):
            self._container.clear()
            with self._container:
                for msg in self._msgs:
                    render_message(msg)
            self._scroll_to_bottom()

    def _scroll_to_bottom(self) -> None:
        if self._container is None:
            return
        with suppress(RuntimeError):
            cid = self._container.id
            ui.run_javascript(f"""
                var el = document.getElementById("{cid}");
                if (el) {{ el.scrollTop = el.scrollHeight; }}
            """)

    def _replace_last(self, role: str, content: str, agent: str) -> None:
        if (
            self._msgs
            and self._msgs[-1].get("agent") == agent
            and self._msgs[-1].get("content") != content
        ):
            self._msgs[-1] = {"role": role, "content": content, "agent": agent}
        elif not self._msgs or self._msgs[-1].get("agent") != agent:
            self._msgs.append({"role": role, "content": content, "agent": agent})
        self._render_all()

    def _process_pending(self) -> None:
        msg = self._orchestrator.take_pending()
        if msg:
            self._add_message("user", msg, "")
            asyncio.ensure_future(self._handle_pending(msg))

    async def _handle_pending(self, text: str) -> None:
        await self._orchestrator.handle_user_input(text)
        self._process_pending()

    def _on_suggestions_received(self, suggestions: list[dict[str, str]]) -> None:
        import logging
        _log = logging.getLogger(__name__)
        _log.info("_on_suggestions_received: %d suggestions, container=%s, editor=%s",
                   len(suggestions), self._container is not None, self._outline_editor is not None)
        if not self._outline_editor or not self._container:
            _log.warning("_on_suggestions_received: missing outline_editor or container")
            return
        card = DiffCard()
        card.suggestions = suggestions
        card.on_confirm(self._apply_suggestions)
        card.on_reject(self._render_all)
        with self._container:
            ui.html(
                '<div class="py-2 text-xs text-center" '
                'style="color:var(--text-tertiary)">'
                '[suggest] AI suggests changes</div>'
            )
            card.build()

    def _apply_suggestions(self, suggestions: list[dict[str, str]]) -> None:
        import logging
        _log = logging.getLogger(__name__)
        content = self._outline_editor.content
        for s in suggestions:
            old_text = s.get("old", "")
            new_text = s.get("new", "")
            section = s.get("section", "")
            applied = False
            if old_text and len(old_text) >= 3 and old_text in content:
                content = content.replace(old_text, new_text, 1)
                applied = True
                _log.info("Applied suggestion: section=%s", section)
            elif section and section in content:
                content = content.replace(section, f"{section}\n{new_text}", 1)
                applied = True
                _log.info("Appended to section: %s", section)
            if not applied:
                _log.warning("Suggestion not matched: section=%s old=%s", section, old_text[:50])
        self._outline_editor.content = content
        _log.info("Outline updated, new length: %d", len(content))
