"""7-stage progress bar for project workflow."""

from nicegui import ui

from ..i18n import status_color, t
from .config import STAGES


def stage_progress(current: str) -> None:
    """Render horizontal stage progress bar."""
    with ui.element("div").classes("flex items-center gap-1"):
        steps = [(s.value, status_color(s.value)) for s in STAGES]
        for i, (value, color) in enumerate(steps):
            _dot(value, color, current == value, _is_done(value, current))
            if i < len(steps) - 1:
                _line(current, value, steps[i + 1][0])


def _is_done(status_value: str, current: str) -> bool:
    """Check if a stage is completed (before current)."""
    values = [s.value for s in STAGES]
    if status_value not in values or current not in values:
        return False
    return values.index(status_value) < values.index(current)


def _dot(value: str, color: str, active: bool, done: bool) -> None:
    """Render a single stage dot with label."""
    with ui.element("div").classes("flex flex-col items-center gap-0.5"):
        size = "w-3 h-3"
        if active:
            cls = f"{size} rounded-full border-2"
            style = f"background:{color};border-color:{color};box-shadow:0 0 6px {color}"
        elif done:
            cls = f"{size} rounded-full"
            style = "background:var(--text-nav-primary)"
        else:
            cls = f"{size} rounded-full border"
            style = "border-color:var(--fg-tertiary)"
        ui.element("div").classes(cls).style(style)
        label = t(f"status.{value}")
        label_cls = "text-[10px] font-medium whitespace-nowrap"
        label_color = "var(--text-nav-primary)" if active or done else "var(--fg-tertiary)"
        ui.label(label).classes(label_cls).style(f"color:{label_color}")


def _line(current: str, from_val: str, to_val: str) -> None:
    """Render connecting line between stage dots."""
    values = [s.value for s in STAGES]
    to_idx = values.index(to_val)
    cur_idx = values.index(current)
    done = to_idx <= cur_idx
    line_color = "var(--text-nav-primary)" if done else "var(--fg-tertiary)"
    ui.element("div").style(
        f"width:24px;height:1px;background:{line_color};margin-bottom:14px"
    )
