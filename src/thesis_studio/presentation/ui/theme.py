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
