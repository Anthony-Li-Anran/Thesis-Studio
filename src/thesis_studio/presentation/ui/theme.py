"""Prism 暗色主题设计令牌与 UI 基础元素。"""

from typing import Any

from nicegui import ui
from nicegui.elements.mixins.text_element import TextElement

_THEME_CSS = """\
<style>
:root {
  --neutral-50: #fff;
  --neutral-100: #e8e8e8;
  --neutral-150: #e2e2e2;
  --neutral-200: #cdcdcd;
  --neutral-300: #afafaf;
  --neutral-400: #999;
  --neutral-450: #737373;
  --neutral-500: #585858;
  --neutral-600: #353535;
  --neutral-700: #2a2a2a;
  --neutral-750: #252525;
  --neutral-800: #1f1f1f;
  --neutral-900: #161616;
  --neutral-950: #000;
  --bg-app: #161616;
  --bg-sidepanel: #1f1f1f;
  --bg-sidepanel-secondary: rgba(39, 40, 41, 0.5);
  --input-bg: #2a2a2a;
  --input-border: #585858;
  --input-border-hover: #999;
  --input-border-active: #999;
  --search-input-border: #585858;
  --search-input-border-hover: #999;
  --search-input-border-active: #999;
  --button-primary-bg: #fff;
  --button-primary-bg-hover: #e8e8e8;
  --button-primary-text: #161616;
  --button-primary-text-hover: #000;
  --button-secondary-bg: #353535;
  --button-secondary-bg-hover: #999;
  --button-secondary-text: #e8e8e8;
  --nav-bg-active: #2a2a2a;
  --nav-bg-hover-strong: #2a2a2a;
  --text-nav-primary: #fff;
  --text-nav-secondary: #afafaf;
  --text-nav-tertiary: #999;
  --text-editor-primary: #fff;
  --text-editor-tertiary: #999;
  --fg-primary: #fff;
  --fg-secondary: #999;
  --fg-tertiary: #585858;
  --border-outline: #1f1f1f;
  --border-log: #2a2a2a;
  --project-list-divider: #2a2a2a;
  --project-list-skeleton-bg: #353535;
  --optionmenu-bg-hover: #353535;
  --bg-body: #0a0a0a;
  color-scheme: dark;
}
html[data-theme="light"] {
  --bg-body: #f5f5f5;
  --bg-app: #f5f5f5;
  --bg-sidepanel: #fff;
  --bg-sidepanel-secondary: rgba(255, 255, 255, 0.5);
  --input-bg: #e8e8e8;
  --input-border: #cdcdcd;
  --input-border-hover: #585858;
  --input-border-active: #585858;
  --search-input-border: #cdcdcd;
  --search-input-border-hover: #585858;
  --search-input-border-active: #585858;
  --button-primary-bg: #161616;
  --button-primary-bg-hover: #353535;
  --button-primary-text: #fff;
  --button-primary-text-hover: #fff;
  --button-secondary-bg: #e8e8e8;
  --button-secondary-bg-hover: #cdcdcd;
  --button-secondary-text: #161616;
  --nav-bg-active: #e8e8e8;
  --nav-bg-hover-strong: #e8e8e8;
  --text-nav-primary: #161616;
  --text-nav-secondary: #585858;
  --text-nav-tertiary: #737373;
  --text-editor-primary: #161616;
  --text-editor-tertiary: #737373;
  --fg-primary: #161616;
  --fg-secondary: #585858;
  --fg-tertiary: #afafaf;
  --border-outline: #e8e8e8;
  --border-log: #e8e8e8;
  --project-list-divider: #e8e8e8;
  --project-list-skeleton-bg: #e8e8e8;
  --optionmenu-bg-hover: #e8e8e8;
  color-scheme: light;
}
html, body, #app { height: 100%; margin: 0; }
.q-layout, .q-page-container, .q-page, .nicegui-content { height: 100%; }
body {
  font-family: CrixetSans, ui-sans-serif, system-ui, sans-serif;
  background-color: var(--bg-body, #0a0a0a);
  color: var(--fg-primary);
}
a { color: inherit; text-decoration: none; }
button {
  border: none;
  cursor: pointer;
  background: transparent;
  color: inherit;
  font-family: inherit;
}
input { outline: none; }
.nicegui-content { padding: 0; }
.q-page { padding: 0; min-height: 0; }
.nicegui-link { color: inherit; text-decoration: none; }

.ts-bg-app { background-color: var(--bg-app); }
.ts-bg-sidepanel { background-color: var(--bg-sidepanel-secondary); }
.ts-bg-input { background-color: var(--input-bg); }
.ts-skeleton-bg { background-color: var(--project-list-skeleton-bg); }
.ts-text-primary { color: var(--fg-primary); }
.ts-text-secondary { color: var(--fg-secondary); }
.ts-text-tertiary { color: var(--fg-tertiary); }
.ts-text-nav { color: var(--text-nav-primary); }
.ts-text-nav-secondary { color: var(--text-nav-secondary); }
.ts-text-editor-primary { color: var(--text-editor-primary); }
.ts-text-editor-tertiary { color: var(--text-editor-tertiary); }
.ts-border-log { border-color: var(--border-log); }
.ts-border-outline { border-color: var(--border-outline); }
.ts-border-divider { border-color: var(--project-list-divider); }
.ts-border-input { border-color: var(--input-border); }
.ts-divide-list > * + * { border-top: 1px solid var(--project-list-divider); }

/* 搜索框交互态 */
.ts-search-input::placeholder { color: var(--text-editor-tertiary); }
.ts-search-input:hover { border-color: var(--search-input-border-hover); }
.ts-search-input:hover::placeholder { color: var(--text-editor-primary); }
.ts-search-input:active { border-color: var(--search-input-border-active); }
.ts-search-input:focus::placeholder { color: transparent; }

/* 骨架屏呼吸动画 */
@keyframes ts-skeleton-breathe {
  0%, to { opacity: 0.68; }
  50% { opacity: 1; }
}
.ts-skeleton-item {
  animation: 1.8s cubic-bezier(0.45, 0, 0.55, 1) infinite ts-skeleton-breathe;
  animation-delay: var(--ts-skeleton-delay, 0s);
}
@media (prefers-reduced-motion: reduce) {
  .ts-skeleton-item { opacity: 0.84; animation: none; }
}

.ts-btn-primary {
  background-color: var(--button-primary-bg);
  color: var(--button-primary-text);
}
.ts-btn-primary:hover {
  background-color: var(--button-primary-bg-hover);
  color: var(--button-primary-text-hover);
}
.ts-btn-secondary {
  background-color: var(--button-secondary-bg);
  color: var(--button-secondary-text);
}
.ts-btn-secondary:hover {
  background-color: var(--button-secondary-bg-hover);
}
/* Override Quasar bg-primary/text-white on QBtn inside dialogs (higher specificity) */
.ts-dialog-card .q-btn.ts-btn-primary {
  background-color: var(--button-primary-bg) !important;
  color: var(--button-primary-text) !important;
}
.ts-dialog-card .q-btn.ts-btn-primary:hover {
  background-color: var(--button-primary-bg-hover) !important;
  color: var(--button-primary-text-hover) !important;
}
.ts-dialog-card .q-btn.ts-btn-secondary {
  background-color: var(--button-secondary-bg) !important;
  color: var(--button-secondary-text) !important;
}
.ts-dialog-card .q-btn.ts-btn-secondary:hover {
  background-color: var(--button-secondary-bg-hover) !important;
}
.ts-nav-active {
  background-color: var(--nav-bg-active);
  color: var(--text-nav-primary);
}
.ts-sign-in:hover {
  background-color: var(--nav-bg-hover-strong);
}
.ts-btn-tertiary {
  background-color: transparent;
  color: var(--text-editor-tertiary);
}
.ts-btn-tertiary:hover {
  background-color: var(--nav-bg-hover-strong);
  color: var(--text-editor-primary);
}
.ts-btn-view-active {
  background-color: var(--optionmenu-bg-hover);
  color: var(--fg-primary);
}
.ts-btn-view-inactive {
  background-color: transparent;
  color: var(--fg-tertiary);
}
.ts-btn-view-inactive:hover {
  background-color: var(--optionmenu-bg-hover);
  color: var(--fg-primary);
}
/* === Dialog card system: clean, minimal, Prism-native === */
.ts-dialog-card {
  background-color: var(--bg-sidepanel);
  border: 1px solid var(--border-outline);
  border-radius: 16px;
  padding: 0;
  box-shadow: 0 24px 64px rgba(0,0,0,0.5);
  overflow: hidden;
}
.ts-dialog-body { padding: 36px; overflow-y: auto; max-height: 90vh; }
.ts-dialog-close {
  position: absolute; top: 16px; right: 16px;
  width: 30px; height: 30px; display: flex;
  align-items: center; justify-content: center;
  color: var(--text-nav-tertiary); cursor: pointer;
  border-radius: 8px; transition: all 0.15s; z-index: 10;
}
.ts-dialog-close:hover { color: var(--text-nav-primary); background: var(--nav-bg-hover-strong); }
.ts-dialog-header { margin-bottom: 28px; }
.ts-dialog-title { font-size: 20px; font-weight: 600; color: var(--text-nav-primary); letter-spacing: -0.01em; }
.ts-dialog-subtitle { font-size: 13px; color: var(--text-nav-tertiary); margin-top: 4px; }
.ts-dialog-form { display: flex; flex-direction: column; gap: 18px; }
.ts-dialog-field { display: flex; flex-direction: column; }
.ts-dialog-label { font-size: 12px; font-weight: 500; color: var(--text-nav-secondary); margin-bottom: 6px; }
.ts-dialog-input { width: 100% !important; }
.ts-dialog-input .q-field__control {
  background-color: var(--input-bg) !important;
  border: 1px solid var(--input-border) !important;
  border-radius: 10px !important; min-height: 42px;
  transition: border-color 0.15s;
}
.ts-dialog-input .q-field__native { color: var(--text-editor-primary); padding: 0 14px; font-size: 14px; }
.ts-dialog-input .q-field__native::placeholder { color: var(--text-editor-tertiary); }
.ts-dialog-input .q-field__control::before, .ts-dialog-input .q-field__control::after { border: none !important; }
.ts-dialog-input.q-field--focused .q-field__control { border-color: var(--input-border-active) !important; }
.ts-dialog-textarea .q-field__control { min-height: 84px !important; align-items: flex-start; padding-top: 10px; }
.ts-dialog-input .q-field__append { padding: 0 10px; cursor: pointer; }
.ts-dialog-error { color: #ef4444; font-size: 13px; min-height: 18px; margin-top: 8px; }
.ts-dialog-footer { display: flex; gap: 10px; justify-content: flex-end; margin-top: 24px; padding-top: 20px; border-top: 1px solid var(--border-outline); }
.ts-dialog-card .q-btn {
  min-height: 42px !important; border-radius: 10px !important;
  text-transform: none !important; padding: 0 20px !important;
  font-weight: 500; font-size: 14px;
}
.ts-dialog-links { display: flex; justify-content: center; align-items: center; gap: 8px; font-size: 13px; margin-top: 20px; }
.ts-dialog-link { color: var(--text-nav-primary); cursor: pointer; transition: opacity 0.15s; user-select: none; }
.ts-dialog-link:hover { opacity: 0.65; }
.ts-dialog-dot { color: var(--text-nav-tertiary); }
.ts-dialog-hint { color: var(--text-nav-secondary); }
.ts-kw-chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.ts-kw-chip {
  display: inline-flex; align-items: center; gap: 2px;
  background: var(--button-secondary-bg); color: var(--button-secondary-text);
  border-radius: 999px; padding: 4px 4px 4px 12px; font-size: 12px; font-weight: 500;
}
.ts-kw-chip-x {
  border: none; background: none; color: inherit; cursor: pointer;
  display: flex; padding: 2px; border-radius: 999px; transition: background 0.15s;
}
.ts-kw-chip-x:hover { background: var(--nav-bg-hover-strong); }
.ts-eye-toggle {
  color: var(--text-editor-tertiary); display: flex; align-items: center;
  transition: color 0.15s; border: none; background: none;
}
.ts-eye-toggle:hover { color: var(--text-editor-primary); }
/* === Settings: larger dialog === */
.ts-settings-dialog { min-width: 720px; max-width: 800px; }
.ts-settings-dialog .ts-dialog-body { padding: 32px; max-height: 85vh; }

/* === Settings: tab navigation === */
.ts-settings-tabs { display: flex; gap: 0; margin-bottom: 28px; border-bottom: 1px solid var(--border-outline); }
.ts-settings-tab { padding: 10px 20px; font-size: 13px; font-weight: 500; color: var(--text-nav-tertiary); cursor: pointer; transition: all 0.15s; border-bottom: 2px solid transparent; background: none; user-select: none; }
.ts-settings-tab:hover { color: var(--text-nav-primary); }
.ts-settings-tab.ts-settings-tab--active { color: var(--text-nav-primary); border-bottom-color: var(--fg-primary); }

/* === Settings: agent dropdown === */
.ts-agent-dropdown { position: relative; }
.ts-agent-dropdown-btn { display: flex; align-items: center; justify-content: space-between; width: 100%; padding: 10px 14px; background: var(--input-bg); border: 1px solid var(--input-border); border-radius: 10px; color: var(--text-editor-primary); font-size: 14px; cursor: pointer; transition: border-color 0.15s; }
.ts-agent-dropdown-btn:hover { border-color: var(--input-border-hover); }
.ts-agent-dropdown-arrow { transition: transform 0.15s; display: inline-flex; }
.ts-agent-dropdown-btn.ts-agent-dropdown--open .ts-agent-dropdown-arrow { transform: rotate(180deg); }
.ts-agent-dropdown-menu { position: absolute; top: 100%; left: 0; right: 0; z-index: 50; background: var(--bg-sidepanel); border: 1px solid var(--border-outline); border-radius: 10px; margin-top: 4px; box-shadow: 0 12px 32px rgba(0,0,0,0.3); overflow: hidden; }
.ts-agent-dropdown-item { display: flex; align-items: center; gap: 8px; padding: 8px 14px; cursor: pointer; transition: background 0.1s; font-size: 13px; color: var(--text-nav-primary); user-select: none; }
.ts-agent-dropdown-item:hover { background: var(--nav-bg-hover-strong); }
.ts-agent-checkbox { width: 16px; height: 16px; border-radius: 4px; border: 1.5px solid var(--input-border); display: flex; align-items: center; justify-content: center; transition: all 0.15s; flex-shrink: 0; }
.ts-agent-checkbox--checked { background: var(--fg-primary); border-color: var(--fg-primary); }
.ts-agent-checkbox svg { width: 10px; height: 10px; color: var(--bg-sidepanel); display: none; }
.ts-agent-checkbox--checked svg { display: block; }
.ts-agent-dropdown-divider { height: 1px; background: var(--border-outline); margin: 4px 0; }
.ts-agent-dropdown-select-all { font-weight: 500; color: var(--text-nav-secondary); }

/* === Settings: external API card === */
.ts-external-api-card { background: var(--bg-sidepanel-secondary); border: 1px solid var(--border-outline); border-radius: 12px; padding: 18px; margin-bottom: 12px; }
.ts-external-api-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.ts-external-api-name { font-size: 15px; font-weight: 600; color: var(--text-nav-primary); }
.ts-external-api-status { font-size: 11px; padding: 3px 8px; border-radius: 999px; font-weight: 500; }
.ts-external-api-status--enabled { background: rgba(34,197,94,0.12); color: #22c55e; }
.ts-external-api-status--disabled { background: rgba(156,163,175,0.12); color: #9ca3af; }
.ts-external-api-fields { display: flex; flex-direction: column; gap: 10px; }
.ts-external-api-row { display: flex; gap: 10px; align-items: flex-end; }
.ts-external-api-row .ts-dialog-field { flex: 1; }

/* === Settings: test button === */
.ts-test-btn { display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px; border-radius: 8px; font-size: 12px; font-weight: 500; cursor: pointer; transition: all 0.15s; background: var(--button-secondary-bg); color: var(--button-secondary-text); border: none; white-space: nowrap; position: relative; }
.ts-test-btn:hover { background: var(--button-secondary-bg-hover); }


/* === Settings: AI config list card === */
.ts-ai-config-card { background: var(--bg-sidepanel-secondary); border: 1px solid var(--border-outline); border-radius: 12px; padding: 16px; margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.ts-ai-config-info { flex: 1; min-width: 0; }
.ts-ai-config-name { font-size: 14px; font-weight: 600; color: var(--text-nav-primary); }
.ts-ai-config-meta { font-size: 12px; color: var(--text-nav-tertiary); margin-top: 2px; }
.ts-ai-config-agents { display: flex; gap: 4px; margin-top: 4px; flex-wrap: wrap; }
.ts-ai-config-agent-tag { font-size: 10px; padding: 2px 6px; border-radius: 999px; background: var(--nav-bg-hover-strong); color: var(--text-nav-secondary); }
.ts-ai-config-actions { display: flex; gap: 6px; align-items: center; flex-shrink: 0; }

/* === Settings: add button area === */
.ts-settings-add-area { display: flex; gap: 8px; margin-top: 16px; }

/* === Settings: external API toggle === */
.ts-external-toggle { display: flex; align-items: center; gap: 8px; cursor: pointer; }
.ts-external-toggle-switch { width: 40px; height: 22px; border-radius: 999px; background: var(--input-border); transition: background 0.15s; position: relative; flex-shrink: 0; }
.ts-external-toggle-switch--on { background: #22c55e; }
.ts-external-toggle-knob { width: 18px; height: 18px; border-radius: 50%; background: #fff; position: absolute; top: 2px; left: 2px; transition: left 0.15s; }
.ts-external-toggle-switch--on .ts-external-toggle-knob { left: 20px; }

</style>
"""


def apply_theme() -> None:
    """注入暗色主题 CSS 并启用暗色模式。"""
    ui.add_head_html(_THEME_CSS)
    ui.dark_mode(True)


def logo() -> None:
    """渲染导航栏 logo（纯文本）。"""
    with ui.link(target="/").classes(
        "cursor-pointer inline-flex items-center gap-1 tracking-tight"
    ):
        ui.label("Thesis").classes("font-bold text-xl ts-text-nav")
        ui.label("Studio").classes("font-extralight text-xl ts-text-nav-secondary")


class TextButton(TextElement):
    """原生 button 元素，支持 text 属性序列化。"""

    def __init__(self, text: str = "", **kwargs: Any) -> None:
        kwargs.setdefault("tag", "button")
        super().__init__(text=text, **kwargs)
