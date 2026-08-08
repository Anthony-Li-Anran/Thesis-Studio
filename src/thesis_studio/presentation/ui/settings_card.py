"""Settings dialog with two tabs: AI API configs and External API configs."""

import asyncio

import httpx
from nicegui import app, ui

from ...domain.models.settings import (
    AGENT_ROLES,
    WORKFLOW_API_DEFAULTS,
    AIConfig,
    ExternalAPIConfig,
    UserSettings,
)
from ...infrastructure.bootstrap import get_current_user_settings_repo
from ...infrastructure.logging import get_logger
from .i18n import t

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# SVG Icons
# ---------------------------------------------------------------------------

_CLOSE_ICON = (
    '<svg fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" '
    'width="18" height="18" xmlns="http://www.w3.org/2000/svg">'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>'
)

_EYE_ICON = (
    '<svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" '
    'width="18" height="18" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639 12.27 12.27 0 015.32-6.046A12.27 12.27 0 0112 4.5c1.668 0 3.282.366 4.737 1.037a12.27 12.27 0 015.32 6.046 1.012 1.012 0 010 .639 12.27 12.27 0 01-5.32 6.046A12.27 12.27 0 0112 19.5c-1.668 0-3.282-.366-4.737-1.037a12.27 12.27 0 01-5.32-6.046z"/>'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>'
)

_EYE_OFF_ICON = (
    '<svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" '
    'width="18" height="18" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.241 19.5 12 19.5c.993 0 1.952-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.272 10.065 7.5a10.461 10.461 0 01-1.532 2.793m-6.218-6.218A3 3 0 1110.5 12a3 3 0 011.515-3.218z"/>'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M3 3l18 18"/></svg>'
)

_TRASH_ICON = (
    '<svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" '
    'width="16" height="16" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0"/></svg>'
)

_EDIT_ICON = (
    '<svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" '
    'width="16" height="16" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10"/></svg>'
)

_GEAR_ICON = (
    '<svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" '
    'width="18" height="18" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
    '<path stroke-linecap="round" stroke-linejoin="round" '
    'd="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z"/>'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>'
)

_CHEVRON_DOWN = (
    '<svg fill="currentColor" width="14" height="14" viewBox="0 0 20 20" '
    'xmlns="http://www.w3.org/2000/svg"><path d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z"/></svg>'
)

_CHECK_ICON = (
    '<svg fill="currentColor" width="10" height="10" viewBox="0 0 20 20" '
    'xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M16.704 4.153a.75.75 0 01.143 1.052l-8 10.5a.75.75 0 01-1.127.075l-4.5-4.5a.75.75 0 011.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 011.05-.143z" clip-rule="evenodd"/></svg>'
)

_TEST_ICON = (
    '<svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" '
    'width="14" height="14" xmlns="http://www.w3.org/2000/svg">'
    '<path stroke-linecap="round" stroke-linejoin="round" d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m13.35-.622l1.757-1.757a4.5 4.5 0 00-6.364-6.364l-4.5 4.5a4.5 4.5 0 001.242 7.244"/></svg>'
)

_PLUS_ICON = (
    '<svg fill="currentColor" width="14" height="14" viewBox="0 0 20 20" '
    'xmlns="http://www.w3.org/2000/svg"><path d="M10.75 4.75a.75.75 0 00-1.5 0v4.5h-4.5a.75.75 0 000 1.5h4.5v4.5a.75.75 0 001.5 0v-4.5h4.5a.75.75 0 000-1.5h-4.5v-4.5z"/></svg>'
)

# ---------------------------------------------------------------------------
# Presets
# ---------------------------------------------------------------------------

_OLLAMA_PRESET = {
    "name": "Ollama Local",
    "endpoint": "http://localhost:11434/v1",
    "key": "ollama",
    "model": "qwen2.5",
}

_OPENAI_PRESET = {
    "name": "OpenAI",
    "endpoint": "https://api.openai.com/v1",
    "key": "",
    "model": "gpt-4o",
}


# ---------------------------------------------------------------------------
# Main entry
# ---------------------------------------------------------------------------

def settings_card() -> ui.dialog:
    """Create settings dialog with two tabs: AI API and External APIs."""
    state = {
        "tab": "ai",
        "view": "list",
        "configs": [],
        "external_apis": [],
        "editing_id": None,
        "content": None,
        "form_agents": [],
        "dropdown_open": False,
    }
    with ui.dialog() as dialog, ui.element("div").classes(
        "ts-dialog-card ts-settings-dialog"
    ):
        with ui.element("div").classes("ts-dialog-body"):
            _close_button(dialog)
            _render(state)
    ui.timer(0, lambda: _init(dialog, state), once=True)
    return dialog


async def _init(dialog: ui.dialog, state: dict) -> None:
    """Load settings from repository and render."""
    repo = get_current_user_settings_repo()
    try:
        user_id = app.storage.user.get("user_id", "")
        is_guest = app.storage.user.get("is_guest", False)
    except RuntimeError:
        user_id = ""
        is_guest = False
    uid = "guest" if is_guest else (user_id or "")
    settings = await repo.get(uid)
    state["configs"] = list(settings.configs)
    state["external_apis"] = list(settings.external_apis) if settings.external_apis else []
    if not state["external_apis"]:
        state["external_apis"] = [
            ExternalAPIConfig(
                service_type=d["service_type"],
                name=d["name"],
                endpoint=d["endpoint"],
                test_url=d.get("test_url", ""),
                needs_key=d.get("needs_key", False),
            )
            for d in WORKFLOW_API_DEFAULTS
        ]
    _render(state)


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

def _render(state: dict) -> None:
    """Re-render settings dialog content."""
    content = state.get("content")
    if content is not None:
        content.clear()
        with content:
            _render_header(state)
            if state["tab"] == "ai":
                _render_ai_tab(state)
            else:
                _render_external_tab(state)
    else:
        with ui.element("div") as wrapper:
            state["content"] = wrapper
            _render_header(state)
            if state["tab"] == "ai":
                _render_ai_tab(state)
            else:
                _render_external_tab(state)


def _render_header(state: dict) -> None:
    """Render tab navigation header."""
    with ui.element("div").classes("ts-dialog-header"):
        ui.label(t("settings.title")).classes("ts-dialog-title")
        with ui.element("div").classes("ts-settings-tabs"):
            for tab_key, tab_label in [("ai", "settings.tab.ai_api"), ("external", "settings.tab.external_apis")]:
                is_active = state["tab"] == tab_key
                cls = "ts-settings-tab"
                if is_active:
                    cls += " ts-settings-tab--active"
                btn = ui.element("button").classes(cls)
                btn.on("click", lambda _, k=tab_key: _switch_tab(state, k))
                with btn:
                    ui.label(t(tab_label))


def _switch_tab(state: dict, tab: str) -> None:
    state["tab"] = tab
    state["view"] = "list"
    state["editing_id"] = None
    state["form_agents"] = []
    _render(state)


# ---------------------------------------------------------------------------
# AI API Tab
# ---------------------------------------------------------------------------

def _render_ai_tab(state: dict) -> None:
    """Render AI API config tab."""
    if state["view"] == "list":
        _render_ai_list(state)
    else:
        _render_ai_form(state)


def _render_ai_list(state: dict) -> None:
    """Render list of AI configs."""
    configs = state["configs"]
    if not configs:
        with ui.element("div").classes("py-8 text-center"):
            ui.label(t("settings.no_configs")).classes("ts-text-nav-secondary text-sm")
    else:
        for cfg in configs:
            _render_ai_config_card(state, cfg)

    with ui.element("div").classes("ts-settings-add-area"):
        ui.button(t("settings.add_local"), on_click=lambda: _open_ai_form(state, "ollama")).classes(
            "ts-btn-secondary"
        ).props("no-caps")
        ui.button(t("settings.add_config"), on_click=lambda: _open_ai_form(state, "openai")).classes(
            "ts-btn-primary"
        ).props("unelevated no-caps")


def _render_ai_config_card(state: dict, cfg: AIConfig) -> None:
    """Render a single AI config card."""
    with ui.element("div").classes("ts-ai-config-card"):
        with ui.element("div").classes("ts-ai-config-info"):
            ui.label(cfg.name).classes("ts-ai-config-name")
            ui.label(f"{cfg.model} — {cfg.api_endpoint}").classes("ts-ai-config-meta")
            if cfg.agents:
                with ui.element("div").classes("ts-ai-config-agents"):
                    for agent in cfg.agents:
                        ui.label(t(f"settings.agent.{agent}")).classes("ts-ai-config-agent-tag")
        with ui.element("div").classes("ts-ai-config-actions"):
            _test_button(state, cfg)
            with ui.element("button").classes("ts-btn-tertiary inline-flex items-center justify-center rounded-full h-[32px] w-[32px]").on(
                "click", lambda _, c=cfg: _open_ai_form(state, None, c)
            ).tooltip(t("settings.edit_config")):
                ui.html(_EDIT_ICON)
            with ui.element("button").classes("ts-btn-tertiary inline-flex items-center justify-center rounded-full h-[32px] w-[32px]").on(
                "click", lambda _, c=cfg: _delete_config(state, c)
            ).tooltip(t("settings.delete_config")):
                ui.html(_TRASH_ICON)


def _open_ai_form(state: dict, provider: str | None, editing_cfg: AIConfig | None = None) -> None:
    """Open the AI config form."""
    state["view"] = "form"
    state["editing_id"] = editing_cfg.id if editing_cfg else None
    state.pop("form_name", None)
    state.pop("form_endpoint", None)
    state.pop("form_key", None)
    state.pop("form_model", None)
    if editing_cfg:
        state["form_agents"] = list(editing_cfg.agents)
    elif provider == "ollama":
        state["form_agents"] = list(AGENT_ROLES)
    else:
        state["form_agents"] = []
    state["form_provider"] = provider
    _render(state)


def _render_ai_form(state: dict) -> None:
    """Render AI config create/edit form."""
    is_new = state["editing_id"] is None
    editing_cfg = None
    if not is_new:
        for c in state["configs"]:
            if c.id == state["editing_id"]:
                editing_cfg = c
                break

    provider = state.get("form_provider", "openai")
    preset = _OLLAMA_PRESET if provider == "ollama" else _OPENAI_PRESET

    name_val = state.get("form_name", editing_cfg.name if editing_cfg else preset["name"])
    endpoint_val = state.get("form_endpoint", editing_cfg.api_endpoint if editing_cfg else preset["endpoint"])
    key_val = state.get("form_key", editing_cfg.api_key if editing_cfg else preset["key"])
    model_val = state.get("form_model", editing_cfg.model if editing_cfg else preset["model"])

    error_label = ui.label("").classes("ts-dialog-error")

    with ui.element("div").classes("ts-dialog-form"):
        name_input = _field(t("settings.field.name"), t("settings.ph.name"), name_val)
        name_input.on("update:model-value", lambda e: state.update({"form_name": str(e.args[0]) if e.args else ""}))
        endpoint_input = _field(t("settings.field.endpoint"), t("settings.ph.endpoint"), endpoint_val)
        endpoint_input.on("update:model-value", lambda e: state.update({"form_endpoint": str(e.args[0]) if e.args else ""}))
        key_input, _ = _key_field(t("settings.field.key"), t("settings.ph.key"), key_val)
        key_input.on("update:model-value", lambda e: state.update({"form_key": str(e.args[0]) if e.args else ""}))
        model_input = _field(t("settings.field.model"), t("settings.ph.model"), model_val)
        model_input.on("update:model-value", lambda e: state.update({"form_model": str(e.args[0]) if e.args else ""}))

        _render_agent_dropdown(state)

        def _save() -> None:
            name = name_input.value.strip()
            endpoint = endpoint_input.value.strip()
            key = key_input.value.strip()
            model = model_input.value.strip()
            if not name:
                error_label.text = t("settings.name_required")
                return
            if not endpoint:
                error_label.text = t("settings.endpoint_required")
                return
            selected = state.get("form_agents", [])
            taken = _get_taken_agents(state, editing_cfg)
            overlap = [a for a in selected if a in taken]
            if overlap:
                overlap_names = [t(f"settings.agent.{a}") for a in sorted(overlap)]
                error_label.text = t("settings.agent_conflict").format(
                    agents=", ".join(overlap_names)
                )
                return
            if is_new:
                new_cfg = AIConfig(
                    name=name, api_endpoint=endpoint, api_key=key,
                    model=model, agents=selected,
                )
                state["configs"].append(new_cfg)
            else:
                if editing_cfg:
                    editing_cfg.name = name
                    editing_cfg.api_endpoint = endpoint
                    editing_cfg.api_key = key
                    editing_cfg.model = model
                    editing_cfg.agents = selected
            _do_persist(state)
            state["view"] = "list"
            state["editing_id"] = None
            state["form_agents"] = []
            state.pop("form_name", None)
            state.pop("form_endpoint", None)
            state.pop("form_key", None)
            state.pop("form_model", None)
            _render(state)

        def _test_save() -> None:
            _save()
            try:
                ui.notify(t("settings.saved"), type="positive", position="top")
            except RuntimeError:
                pass

        with ui.element("div").classes("ts-dialog-footer"):
            ui.button(t("settings.cancel"), on_click=lambda: _back_to_list(state)).classes(
                "ts-btn-secondary"
            ).props("no-caps")
            ui.button(
                t("settings.save_config") if is_new else t("settings.edit_config"),
                on_click=_test_save,
            ).classes("ts-btn-primary").props("unelevated no-caps")


# ---------------------------------------------------------------------------
# Agent Dropdown
# ---------------------------------------------------------------------------

def _render_agent_dropdown(state: dict) -> None:
    """Render agent dropdown checkbox menu."""
    selected = state.get("form_agents", [])
    all_selected = len(selected) == len(AGENT_ROLES)

    display_text = ", ".join([t(f"settings.agent.{a}") for a in selected]) if selected else t("settings.field.agents")

    with ui.element("div").classes("ts-dialog-field"):
        ui.label(t("settings.field.agents")).classes("ts-dialog-label")
        with ui.element("div").classes("ts-agent-dropdown"):
            btn = ui.element("button").classes("ts-agent-dropdown-btn")
            btn.on("click", lambda: _toggle_dropdown(state))
            with btn:
                ui.label(display_text).classes("truncate flex-1 text-left")
                ui.html(_CHEVRON_DOWN).classes("ts-agent-dropdown-arrow")

            if state.get("dropdown_open"):
                with ui.element("div").classes("ts-agent-dropdown-menu"):
                    _dropdown_item(
                        state, t("settings.select_all") if not all_selected else t("settings.deselect_all"),
                        lambda: _select_all_agents(state),
                        is_select_all=True,
                    )
                    ui.element("div").classes("ts-agent-dropdown-divider")
                    for agent in AGENT_ROLES:
                        is_checked = agent in selected
                        _dropdown_item(
                            state, t(f"settings.agent.{agent}"),
                            lambda a=agent: _toggle_agent(state, a),
                            is_checked=is_checked,
                        )


def _dropdown_item(state: dict, label: str, handler, is_checked: bool = False, is_select_all: bool = False) -> None:
    """Render a single dropdown item."""
    item = ui.element("div").classes("ts-agent-dropdown-item")
    if is_select_all:
        item.classes("ts-agent-dropdown-select-all")
    item.on("click", lambda: handler())
    with item:
        with ui.element("div").classes(
            f"ts-agent-checkbox{' ts-agent-checkbox--checked' if is_checked else ''}"
        ):
            ui.html(_CHECK_ICON)
        ui.label(label)


def _toggle_dropdown(state: dict) -> None:
    state["dropdown_open"] = not state.get("dropdown_open", False)
    _render(state)


def _toggle_agent(state: dict, agent: str) -> None:
    selected = state.get("form_agents", [])
    if agent in selected:
        selected.remove(agent)
    else:
        selected.append(agent)
    state["form_agents"] = selected
    state["dropdown_open"] = True
    _render(state)


def _select_all_agents(state: dict) -> None:
    selected = state.get("form_agents", [])
    if len(selected) == len(AGENT_ROLES):
        state["form_agents"] = []
    else:
        state["form_agents"] = list(AGENT_ROLES)
    state["dropdown_open"] = True
    _render(state)


# ---------------------------------------------------------------------------
# External APIs Tab
# ---------------------------------------------------------------------------

def _render_external_tab(state: dict) -> None:
    """Render external APIs tab."""
    external_apis = state["external_apis"]
    if not external_apis:
        with ui.element("div").classes("py-8 text-center"):
            ui.label(t("settings.external.empty")).classes("ts-text-nav-secondary text-sm")
    else:
        for api in external_apis:
            _render_external_api_card(state, api)

    with ui.element("div").classes("ts-dialog-footer"):
        ui.button(t("settings.save_config"), on_click=lambda: _save_external(state)).classes(
            "ts-btn-primary"
        ).props("unelevated no-caps")


def _render_external_api_card(state: dict, api: ExternalAPIConfig) -> None:
    """Render a single external API card."""
    with ui.element("div").classes("ts-external-api-card"):
        with ui.element("div").classes("ts-external-api-header"):
            ui.label(api.name).classes("ts-external-api-name")
            with ui.element("div").classes("flex items-center gap-3"):
                status_cls = "ts-external-api-status ts-external-api-status--enabled" if api.enabled else "ts-external-api-status ts-external-api-status--disabled"
                ui.label(t("settings.external.field.enabled") if api.enabled else "Disabled").classes(status_cls)
                _test_external_button(api)

        with ui.element("div").classes("ts-external-api-fields"):
            with ui.element("div").classes("ts-external-api-row"):
                with ui.element("div").classes("ts-dialog-field flex-1"):
                    ui.label(t("settings.external.field.endpoint")).classes("ts-dialog-label")
                    ui.label(api.endpoint).classes("ts-text-nav-secondary text-sm py-2")

                if api.needs_key:
                    with ui.element("div").classes("ts-dialog-field flex-1"):
                        ui.label(t("settings.external.field.key")).classes("ts-dialog-label")
                        key_input = ui.input(value=api.api_key).classes("ts-dialog-input").props("dark dense type=password")
                        key_input.on("update:model-value", lambda e, a=api: _update_external_key(a, str(e.args[0] if e.args else "")))

            with ui.element("div").classes("ts-external-toggle"):
                toggle = ui.element("div").classes(
                    f"ts-external-toggle-switch{' ts-external-toggle-switch--on' if api.enabled else ''}"
                )
                toggle.on("click", lambda a=api: _toggle_external(state, a))
                with toggle:
                    ui.element("div").classes("ts-external-toggle-knob")
                ui.label(t("settings.external.field.enabled")).classes("ts-dialog-label cursor-pointer")


def _update_external_key(api: ExternalAPIConfig, value: str) -> None:
    api.api_key = value


def _toggle_external(state: dict, api: ExternalAPIConfig) -> None:
    api.enabled = not api.enabled
    _render(state)


def _save_external(state: dict) -> None:
    _do_persist(state)
    try:
        ui.notify(t("settings.saved"), type="positive", position="top")
    except RuntimeError:
        pass
    _render(state)


# ---------------------------------------------------------------------------
# Test connectivity
# ---------------------------------------------------------------------------

def _test_button(state: dict, cfg: AIConfig) -> None:
    btn = ui.element("button").classes("ts-test-btn")
    with btn:
        ui.html(_TEST_ICON)
        ui.label(t("settings.test")).classes("ts-test-label")

    def _on_click():
        try:
            base = cfg.api_endpoint.rstrip("/")
            headers = {}
            if cfg.api_key and cfg.api_key not in ("ollama", ""):
                headers["Authorization"] = f"Bearer {cfg.api_key}"
            with httpx.Client(timeout=5.0) as c:
                resp = c.get(f"{base}/models", headers=headers)
            if 200 <= resp.status_code < 300:
                ui.notify(t("settings.test_success"), type="positive", position="top")
            elif resp.status_code in (401, 403):
                ui.notify(t("settings.test_failed").format(error=f"Auth ({resp.status_code})"), type="warning", position="top")
            else:
                ui.notify(t("settings.test_failed").format(error=f"HTTP {resp.status_code}"), type="negative", position="top")
        except httpx.TimeoutException:
            ui.notify(t("settings.test_failed").format(error="Timeout"), type="negative", position="top")
        except Exception as e:
            ui.notify(t("settings.test_failed").format(error=str(e)), type="negative", position="top")

    btn.on("click", _on_click)
    btn.tooltip(t("settings.test"))


def _test_external_button(api: ExternalAPIConfig) -> None:
    btn = ui.element("button").classes("ts-test-btn")
    with btn:
        ui.html(_TEST_ICON)
        ui.label(t("settings.test")).classes("ts-test-label")

    def _on_click():
        try:
            test_url = api.test_url or api.endpoint.rstrip("/")
            headers = {}
            if api.api_key:
                headers["x-api-key"] = api.api_key
            with httpx.Client(timeout=5.0) as c:
                resp = c.get(test_url, headers=headers)
            if 200 <= resp.status_code < 300:
                ui.notify(t("settings.test_success"), type="positive", position="top")
            else:
                ui.notify(t("settings.test_failed").format(error=f"HTTP {resp.status_code}"), type="negative", position="top")
        except httpx.TimeoutException:
            ui.notify(t("settings.test_failed").format(error="Timeout"), type="negative", position="top")
        except Exception as e:
            ui.notify(t("settings.test_failed").format(error=str(e)), type="negative", position="top")

    btn.on("click", _on_click)
    btn.tooltip(t("settings.test"))


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def _do_persist(state: dict) -> None:
    """Persist settings - capture user in UI context, then save async."""
    try:
        user_id = app.storage.user.get("user_id", "")
        is_guest = app.storage.user.get("is_guest", False)
    except RuntimeError:
        user_id = ""
        is_guest = False
    uid = "guest" if is_guest else (user_id or "")

    async def _save():
        repo = get_current_user_settings_repo()
        settings = UserSettings(
            user_id=uid,
            configs=list(state["configs"]),
            external_apis=list(state["external_apis"]),
        )
        await repo.save(settings)

    asyncio.ensure_future(_save())


def _delete_config(state: dict, cfg: AIConfig) -> None:
    state["configs"] = [c for c in state["configs"] if c.id != cfg.id]
    _do_persist(state)
    _render(state)
    try:
        ui.notify(t("settings.saved"), type="positive", position="top")
    except RuntimeError:
        pass


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _back_to_list(state: dict) -> None:
    state["view"] = "list"
    state["editing_id"] = None
    state["form_agents"] = []
    state["dropdown_open"] = False
    state.pop("form_name", None)
    state.pop("form_endpoint", None)
    state.pop("form_key", None)
    state.pop("form_model", None)
    _render(state)


def _get_taken_agents(state: dict, exclude: AIConfig | None) -> set[str]:
    taken: set[str] = set()
    for c in state["configs"]:
        if exclude and c.id == exclude.id:
            continue
        taken.update(c.agents)
    return taken


def _field(label: str, placeholder: str, value: str = "") -> ui.input:
    with ui.element("div").classes("ts-dialog-field"):
        ui.label(label).classes("ts-dialog-label")
        inp = ui.input(placeholder=placeholder, value=value).classes("ts-dialog-input")
        inp.props("dark dense")
        return inp


def _key_field(label: str, placeholder: str, value: str) -> tuple[ui.input, ui.element]:
    with ui.element("div").classes("ts-dialog-field"):
        ui.label(label).classes("ts-dialog-label")
        with ui.element("div").classes("relative"):
            inp = ui.input(placeholder=placeholder, value=value).classes(
                "ts-dialog-input w-full"
            ).props("dark dense type=password")
            toggle = ui.element("button").classes(
                "absolute right-2 top-1/2 -translate-y-1/2"
                " inline-flex items-center justify-center rounded-full"
                " h-[28px] w-[28px] ts-btn-tertiary"
            )

            def _toggle() -> None:
                is_pass = inp.props.get("type") == "password"
                inp.props["type"] = "text" if is_pass else "password"
                inp.update()
                toggle.clear()
                with toggle:
                    ui.html(_EYE_OFF_ICON if is_pass else _EYE_ICON)

            toggle.on("click", _toggle)
            with toggle:
                ui.html(_EYE_ICON)
        return inp, toggle


def _close_button(dialog: ui.dialog) -> None:
    btn = ui.element("div").classes("ts-dialog-close")
    btn.on("click", dialog.close)
    with btn:
        ui.html(_CLOSE_ICON)


def gear_icon() -> str:
    return _GEAR_ICON
