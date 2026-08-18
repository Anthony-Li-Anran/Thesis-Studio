"""WeChat-style chat room with @mention support, streaming, and suggestion buttons."""

from __future__ import annotations

import json
import asyncio
from collections.abc import Callable
from contextlib import suppress
from typing import Any

from nicegui import ui

from ..i18n import get_lang
from ..i18n import t as _t
from .config import AGENT_COLORS, AGENT_LABELS

GraphCallback = Callable[[list[dict[str, Any]], list[dict[str, Any]]], None]

_SEND_ARROW = (
    '<svg fill="none" viewBox="0 0 24 24" stroke-width="2"'
    ' stroke="currentColor" width="18" height="18"'
    ' xmlns="http://www.w3.org/2000/svg">'
    '<path stroke-linecap="round" stroke-linejoin="round"'
    ' d="M4.5 10.5L12 3m0 0l7.5 7.5M12 3v18"/></svg>'
)

_PROGRESS_ICONS: dict[str, str] = {
    "thinking": "💭",
    "searching": "🔍",
    "found": "📚",
    "clustering": "📊",
    "writing": "📝",
    "error": "⚠️",
}

_MD_CSS = """<style>
.ts-chat-md h1, .ts-chat-md h2, .ts-chat-md h3 {
  font-size: 0.95rem; font-weight: 600; margin: 0.5em 0 0.25em;
  line-height: 1.3;
}
.ts-chat-md h3 { font-size: 0.85rem; }
.ts-chat-md p { margin: 0.25em 0; line-height: 1.5; }
.ts-chat-md ul, .ts-chat-md ol { margin: 0.25em 0; padding-left: 1.2em; }
.ts-chat-md li { margin: 0.1em 0; }
.ts-chat-md a { color: #60a5fa; text-decoration: underline; }
.ts-chat-md strong { font-weight: 600; }
.ts-chat-md code { font-size: 0.8rem; }
</style>"""



class ChatRoom:
    """Chat room component managing messages, input, and suggestion buttons."""

    def __init__(self) -> None:
        self._messages: list[dict[str, str]] = []
        self._container: ui.element | None = None
        self._current_suggestions: list[dict[str, str]] = []
        self._input: ui.input | None = None
        self._agent_service: Any = None
        self._project_id: str = ""
        self._on_review_callback: Callable[[str, str], None] | None = None
        self._on_graph_callback: GraphCallback | None = None
        self._on_save_callback: Callable[[], None] | None = None

    @property
    def agent_service(self) -> Any:
        return self._agent_service

    @agent_service.setter
    def agent_service(self, svc: Any) -> None:
        self._agent_service = svc

    @property
    def project_id(self) -> str:
        return self._project_id

    @project_id.setter
    def project_id(self, pid: str) -> None:
        self._project_id = pid

    def get_session_data(self) -> dict[str, Any]:
        """Return accumulated session state for persistence."""
        if self._agent_service is not None:
            return self._agent_service.get_session_data()
        return {}

    def on_review(self, callback: Callable[[str, str], None]) -> None:
        self._on_review_callback = callback

    def on_graph(self, callback: GraphCallback) -> None:
        self._on_graph_callback = callback

    def on_save(self, callback: Callable[[], None]) -> None:
        self._on_save_callback = callback

    def build(self) -> None:
        """Render the full chat room."""
        with ui.element("div").style("display:flex;flex-direction:column;height:100%"):
            self._container = ui.element("div").classes(
                "px-4 py-4 space-y-3"
            ).style("flex:1;overflow-y:auto;min-height:0")
            self._input = _build_input_area(self._on_send)

    def add_message(self, role: str, content: str, agent: str = "") -> None:
        self._messages.append({"role": role, "content": content, "agent": agent})
        with suppress(RuntimeError):
            self._render_messages()

    def _replace_last(self, role: str, content: str, agent: str = "") -> None:
        if self._messages:
            self._messages[-1] = {"role": role, "content": content, "agent": agent}
        else:
            self._messages.append({"role": role, "content": content, "agent": agent})
        with suppress(RuntimeError):
            self._render_messages()

    def _clear_suggestions(self) -> None:
        """Remove all suggestion buttons."""
        self._current_suggestions = []
        with suppress(RuntimeError):
            self._render_messages()

    def _render_suggestions(self, suggestions: list[dict[str, str]]) -> None:
        """Store suggestions and re-render them inside the message container."""
        self._current_suggestions = suggestions
        with suppress(RuntimeError):
            self._render_messages()

    def _trigger_suggestion(self, action_text: str) -> None:
        """Send a suggestion action as if the user typed it."""
        if self._input is None:
            return
        with suppress(RuntimeError):
            self._input.value = action_text
        ui.timer(0.05, lambda: asyncio.create_task(self._on_send()), once=True)

    async def _on_send(self) -> None:
        """Handle user sending a message — stream agent progress."""
        if self._input is None:
            return
        text = (self._input.value or "").strip()
        if not text:
            return
        with suppress(RuntimeError):
            self.add_message("user", text)
            self._input.value = ""
            self._clear_suggestions()

        if self._agent_service is None:
            return

        progress_count = 0

        try:
            async for event_str in self._agent_service.stream_message(
                text, "researcher", {
                    "topic": "",
                    "project_id": self._project_id,
                    "lang": get_lang(),
                    "history": [
                        {"role": "user" if m["role"] == "user" else "ai", "content": m["content"]}
                        for m in self._messages[-10:]
                    ],
                }
            ):
                try:
                    event = json.loads(event_str)
                except json.JSONDecodeError:
                    continue

                etype = event.get("type", "")

                if etype in ("thinking", "searching", "found", "clustering", "writing"):
                    icon = _PROGRESS_ICONS.get(etype, "●")
                    content = event.get("content", "")
                    if progress_count == 0:
                        self.add_message("researcher", f"{icon} {content}", "researcher")
                    else:
                        self._replace_last("researcher", f"{icon} {content}", "researcher")
                    progress_count += 1

                elif etype == "message":
                    if progress_count > 0:
                        self._messages.pop()
                        progress_count = 0
                    self.add_message("researcher", event.get("content", ""), "researcher")
                    suggestions = event.get("suggestions", [])
                    if suggestions:
                        self._render_suggestions(suggestions)
                    if self._on_save_callback:
                        self._on_save_callback()

                elif etype == "review":
                    html_content = event.get("html_content", "")
                    topic = event.get("topic", "")
                    if html_content and self._on_review_callback:
                        self._on_review_callback(
                            topic,
                            html_content,
                        )

                elif etype == "graph":
                    clusters = event.get("clusters", [])
                    papers = event.get("papers", [])
                    if clusters and self._on_graph_callback:
                        self._on_graph_callback(clusters, papers)

                elif etype == "error":
                    if progress_count > 0:
                        self._messages.pop()
                        progress_count = 0
                    self.add_message(
                        "researcher",
                        f"⚠️ {event.get('content', 'Unknown error')}",
                        "researcher",
                    )

                elif etype == "done":
                    pass

        except RuntimeError:
            pass
        except Exception:
            if progress_count > 0:
                self._messages.pop()
            with suppress(RuntimeError):
                zh = get_lang() == "zh"
                self.add_message("researcher",
                    "“抱歉，处理请求时出错，请重试。”" if zh else "Sorry, request failed. Please retry.",
                    "researcher")
            if self._on_save_callback:
                self._on_save_callback()

    def _render_messages(self) -> None:
        if self._container is None:
            return
        with suppress(RuntimeError):
            self._container.clear()
            with self._container:
                for msg in self._messages:
                    _message_bubble(msg)
                if self._current_suggestions:
                    _render_suggestion_buttons(
                        self._current_suggestions, self._trigger_suggestion
                    )
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


def _build_input_area(on_send: Callable[..., Any]) -> ui.input:
    with ui.element("div").classes(
        "flex items-center gap-2 px-4 py-3 border-t ts-border-divider"
    ):
        inp = (
            ui.input(placeholder=_t("exploring.input_placeholder"))
            .classes("ts-dialog-input flex-1")
            .props("dark dense")
        )
        inp.on("keydown.enter", lambda e: on_send())

        send_btn = ui.element("button").classes(
            "ts-btn-tertiary inline-flex items-center justify-center"
            " rounded-full h-[38px] w-[38px] flex-none"
        )
        send_btn.on("click", lambda e: on_send())
        with send_btn:
            ui.html(_SEND_ARROW)
    return inp


def _message_bubble(msg: dict[str, str]) -> None:
    is_user = msg["role"] == "user"
    is_progress = msg.get("agent") == "researcher" and _is_progress_msg(msg["content"])
    align = "justify-end" if is_user else "justify-start"
    with ui.element("div").classes(f"flex {align} gap-2"):
        if not is_user:
            _agent_avatar(msg.get("agent", "researcher"))
        with ui.element("div").classes("max-w-[75%]"):
            if not is_user and msg.get("agent"):
                color = AGENT_COLORS.get(msg["agent"], "#999")
                label = AGENT_LABELS.get(msg["agent"], msg["agent"])
                ui.label(label).classes("text-xs font-medium").style(f"color:{color}")
            if is_progress:
                ui.label(msg["content"]).classes(
                    "ts-bg-sidepanel rounded-xl px-4 py-2 text-xs italic opacity-70"
                )
            elif is_user:
                ui.label(msg["content"]).classes(
                    "ts-bg-input rounded-xl px-4 py-2.5 text-sm text-right"
                )
            else:
                with ui.element("div").classes(
                    "ts-bg-sidepanel rounded-xl px-4 py-2.5 text-sm ts-chat-md"
                ):
                    ui.add_head_html(_MD_CSS)
                    ui.markdown(msg["content"])
        if is_user:
            _user_avatar()


def _is_progress_msg(content: str) -> bool:
    return any(content.startswith(f"{icon} ") for icon in _PROGRESS_ICONS.values())


def _agent_avatar(agent: str) -> None:
    color = AGENT_COLORS.get(agent, "#999")
    label = AGENT_LABELS.get(agent, agent)
    with ui.element("div").classes(
        "w-7 h-7 rounded-full flex items-center justify-center"
        " flex-none text-xs font-bold"
    ).style(f"background:{color};color:#fff"):
        ui.label(label[:1])


def _render_suggestion_buttons(
    suggestions: list[dict[str, str]],
    on_trigger: Callable[[str], None],
) -> None:
    """Render suggestion buttons inside the message flow."""
    with ui.element("div").classes("flex justify-start gap-2 pl-9"), ui.element("div").classes("flex flex-wrap gap-2"):  # noqa: E501, SIM117
            for s in suggestions:
                label = s.get("label", "?")
                action = s.get("action_text", label)
                btn = ui.element("button").classes(
                    "ts-btn-tertiary text-xs rounded-full px-3 py-1.5"
                    " border ts-border-divider hover:ts-bg-input"
                    " transition-colors cursor-pointer"
                )
                btn.on("click", lambda _a=action: on_trigger(_a))
                with btn:
                    ui.label(label).classes("text-xs")


def _user_avatar() -> None:
    with ui.element("div").classes(
        "w-7 h-7 rounded-full flex items-center justify-center"
        " flex-none text-xs font-bold"
    ).style("background:var(--fg-tertiary);color:var(--bg-app)"):
        ui.label("Y")
