"""DESIGNING phase page: multi-agent chat + outline editor."""

from __future__ import annotations

import asyncio
from typing import Any

from nicegui import ui

from ....domain.models.project import ProjectStatus
from ....domain.workflow.granularity_check import check_outline_granularity
from ....infrastructure.bootstrap import get_current_user_repo, get_llm_for_agent
from ..i18n import get_lang, t, toggle_lang
from ..theme import apply_theme, logo
from .checklist import Checklist
from .designing_chat import DesigningChatRoom
from .format_requirements import FormatRequirementsDrawer
from .outline_editor import OutlineEditor

_CHEVRON_LEFT = (
    '<svg fill="currentColor" width="16" height="16" viewBox="0 0 20 20"'
    ' xmlns="http://www.w3.org/2000/svg"><path d="M12.4707 15.2792C12.7304'
    " 15.5389 12.7304 15.9609 12.4707 16.2206C12.211 16.4803 11.789 16.4803"
    " 11.5293 16.2206L5.7793 10.4706L5.69434 10.3661C5.52383 10.108 5.55103"
    " 9.75655 5.7793 9.52929L11.5293 3.77929L11.6338 3.69433C11.8919 3.52482"
    " 12.2434 3.55202 12.4707 3.77929C12.698 4.00656 12.7282 4.35807 12.5577"
    ' 4.6162L12.4727 4.7207L7.19141 10L12.4707 15.2792Z"></path></svg>'
)

_SUN_ICON = '<svg fill="currentColor" width="16" height="16" viewBox="0 0 20 20"><path d="M10 3.5C10.3452 3.5 10.625 3.77982 10.625 4.125V5.375C10.625 5.72018 10.3452 6 10 6C9.65482 6 9.375 5.72018 9.375 5.375V4.125C9.375 3.77982 9.65482 3.5 10 3.5ZM10 14C10.3452 14 10.625 14.2798 10.625 14.625V15.875C10.625 16.2202 10.3452 16.5 10 16.5C9.65482 16.5 9.375 16.2202 9.375 15.875V14.625C9.375 14.2798 9.65482 14 10 14ZM10 7C8.34315 7 7 8.34315 7 10C7 11.6569 8.34315 13 10 13C11.6569 13 13 11.6569 13 10C13 8.34315 11.6569 7 10 7ZM4.125 10.625C3.77982 10.625 3.5 10.3452 3.5 10C3.5 9.65482 3.77982 9.375 4.125 9.375H5.375C5.72018 9.375 6 9.65482 6 10C6 10.3452 5.72018 10.625 5.375 10.625H4.125ZM14.625 10.625C14.2798 10.625 14 10.3452 14 10C14 9.65482 14.2798 9.375 14.625 9.375H15.875C16.2202 9.375 16.5 9.65482 16.5 10C16.5 10.3452 16.2202 10.625 15.875 10.625H14.625ZM5.75736 5.75736C6.00144 5.51328 6.00144 5.11655 5.75736 4.87247C5.51328 4.62839 5.11655 4.62839 4.87247 4.87247L3.98871 5.75623C3.74463 6.00031 3.74463 6.39704 3.98871 6.64112C4.23279 6.8852 4.62952 6.8852 4.8736 6.64112L5.75736 5.75736ZM15.1275 13.3589C15.3716 13.1148 15.7683 13.1148 16.0124 13.3589L16.8962 14.2426C17.1403 14.4867 17.1403 14.8834 16.8962 15.1275C16.6521 15.3716 16.2554 15.3716 16.0113 15.1275L15.1275 14.2438C14.8834 13.9997 14.8834 13.603 15.1275 13.3589ZM14.2426 5.75736C14.4867 5.51328 14.8834 5.51328 15.1275 5.75736L16.0113 6.64112C16.2554 6.8852 16.2554 7.28193 16.0113 7.52601C15.7672 7.77009 15.3705 7.77009 15.1264 7.52601L14.2426 6.64225C13.9985 6.39817 13.9985 6.00144 14.2426 5.75736ZM4.87247 15.1275C4.62839 14.8835 4.62839 14.4867 4.87247 14.2426L5.75623 13.3589C6.00031 13.1148 6.39704 13.1148 6.64112 13.3589C6.8852 13.603 6.8852 13.9997 6.64112 14.2438L5.75736 15.1275C5.51328 15.3716 5.11655 15.3716 4.87247 15.1275Z"></path></svg>'

_MOON_ICON = '<svg fill="currentColor" width="16" height="16" viewBox="0 0 20 20"><path d="M16.3589 13.1055C15.941 14.257 15.2225 15.2741 14.283 16.044C13.3436 16.814 12.2194 17.309 11.0068 17.475C9.79422 17.641 8.54114 17.4715 7.39942 16.9851C6.2577 16.4986 5.27144 15.7131 4.54975 14.7135C3.82806 13.7139 3.39793 12.5378 3.30399 11.3111C3.21004 10.0845 3.45572 8.85373 4.01463 7.75141C4.57355 6.64909 5.42482 5.71714 6.48069 5.05547C7.53657 4.3938 8.75782 4.02693 10.0105 3.99348C10.3141 3.98614 10.618 4.02782 10.9122 4.11776C10.3708 4.99472 10.0872 6.00763 10.0938 7.04024C10.1004 8.07285 10.397 9.08236 10.9498 9.95296C11.5026 10.8236 12.2891 11.5201 13.22 11.9648C14.151 12.4095 15.189 12.5844 16.2136 12.4694C16.3198 12.4574 16.425 12.439 16.5288 12.4143C16.4749 12.6478 16.406 12.8772 16.3224 13.1013L16.3589 13.1055Z"></path></svg>'

_DEFAULT_OUTLINE = """# 论文题目

## 1 绪论
### 1.1 研究背景

### 1.2 研究问题

### 1.3 研究意义

## 2 文献综述
### 2.1 理论基础

### 2.2 核心概念界定

### 2.3 相关研究述评

### 2.4 研究空白与本研究的理论框架

## 3 研究设计
### 3.1 研究范式

### 3.2 研究假设

### 3.3 实验/调查方案

### 3.4 数据来源与采集

### 3.5 分析方法

## 4 预期结果
### 4.1 预期数据产出

### 4.2 预期分析结果

### 4.3 理论贡献预期

## 5 讨论框架
### 5.1 结果解读方向

### 5.2 与文献对话方向

### 5.3 局限性预判

## 6 结论
### 6.1 研究总结

### 6.2 创新与贡献

### 6.3 未来方向
"""


_THEME_JS = """<script>
function tsInitTheme() {
  const themeBtn = document.getElementById('ts-theme-toggle');
  if (!themeBtn) return false;
  if (themeBtn.dataset.tsBound) return true;
  themeBtn.dataset.tsBound = '1';
  themeBtn.addEventListener('click', function() {
    const html = document.documentElement;
    const sun = document.getElementById('ts-icon-sun');
    const moon = document.getElementById('ts-icon-moon');
    const isLight = html.getAttribute('data-theme') === 'light';
    if (isLight) {
      html.removeAttribute('data-theme');
      if (sun) sun.style.display = '';
      if (moon) moon.style.display = 'none';
    } else {
      html.setAttribute('data-theme', 'light');
      if (sun) sun.style.display = 'none';
      if (moon) moon.style.display = '';
    }
  });
  return true;
}
function tsTryInitTheme() {
  if (tsInitTheme()) return;
  const obs = new MutationObserver(function() {
    if (tsInitTheme()) obs.disconnect();
  });
  obs.observe(document.body, { childList: true, subtree: true });
}
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', tsTryInitTheme);
} else { tsTryInitTheme(); }
</script>"""


@ui.page("/project/{project_id}/designing", title="Thesis Studio")
def designing_page(project_id: str) -> None:
    """DESIGNING phase page entry."""
    apply_theme()
    ui.add_body_html(_THEME_JS)
    ui.timer(0, lambda: _build_page(project_id), once=True)


async def _build_page(project_id: str) -> None:
    project = await get_current_user_repo().get(project_id)
    if project is None:
        _not_found()
        return

    state: dict[str, Any] = {"outline": _DEFAULT_OUTLINE, "template": "imrad", "messages": []}
    saved = project.exploring_state
    if saved:
        state["outline"] = str(saved.get("outline", _DEFAULT_OUTLINE))
        state["messages"] = saved.get("messages", [])

    outline_editor = OutlineEditor()
    outline_editor.content = state["outline"]

    checklist = Checklist()
    format_drawer = FormatRequirementsDrawer()

    def _on_outline_change(content: str) -> None:
        state["outline"] = content
        status = checklist.auto_detect(content)
        checklist.set_all_status(status)

    outline_editor.on_change(_on_outline_change)

    def _on_format_confirm(template: str, custom: str) -> None:
        state["template"] = template
        ui.notify(t("designing.template_applied"), type="positive")

    format_drawer.on_confirm(_on_format_confirm)

    # Root layout
    with ui.element("div").style(
        "position:fixed;top:0;left:0;right:0;bottom:0;"
        "display:flex;flex-direction:column;overflow:hidden"
    ):
        _build_header(project_id, format_drawer)
        with ui.element("div").style("flex:1;min-height:0;display:flex;overflow:hidden"):
            with (
                ui.element("div")
                .classes("w-[35%] border-r ts-border-divider")
                .style("display:flex;flex-direction:column;min-height:0")
            ):
                chat = DesigningChatRoom(outline_editor)
                chat.build()
                # Load saved messages
                for msg in state["messages"]:
                    if isinstance(msg, dict):
                        chat._add_message(
                            msg.get("role", "user"),
                            msg.get("content", ""),
                            msg.get("agent", ""),
                        )
            with (
                ui.element("div")
                .classes("w-[65%]")
                .style("display:flex;flex-direction:column;min-height:0")
            ):
                checklist.build()
                outline_editor.build()
        _build_footer(project_id, state, checklist, chat)


def _build_header(project_id: str, format_drawer: FormatRequirementsDrawer) -> None:
    with ui.element("div").classes(
        "flex items-center justify-between px-5 py-3 border-b ts-border-divider"
    ):
        with ui.element("div").classes("flex items-center gap-3"):
            with ui.link(target="/").classes(
                "ts-btn-tertiary inline-flex items-center justify-center"
                " rounded-full h-[38px] w-[38px]"
            ):
                ui.html(_CHEVRON_LEFT)
            logo()
        with ui.element("div").classes("flex-1 flex justify-center"):
            _stage_progress(ProjectStatus.DESIGNING.value)
        with ui.element("div").classes("flex items-center gap-2"):
            ui.button(icon="description", on_click=lambda: format_drawer.open()).props(
                "flat round dense"
            ).tooltip(t("designing.format_requirements"))
            _library_btn(project_id)
            _theme_toggle_button()
            _lang_btn()


def _stage_progress(current: str) -> None:
    from ..exploring.config import STAGES

    def _status_color(s: str) -> str:
        colors = {
            "init": "#9ca3af",
            "exploring": "#2563eb",
            "designing": "#7c3aed",
            "researching": "#ea580c",
            "writing": "#16a34a",
            "polishing": "#db2777",
            "completed": "#16a34a",
        }
        return colors.get(s, "#9ca3af")

    def _is_done(v: str, cur: str) -> bool:
        values = [s.value for s in STAGES]
        return v in values and cur in values and values.index(v) < values.index(cur)

    with ui.element("div").classes("flex items-center gap-1"):
        for i, s in enumerate(STAGES):
            v, color = s.value, _status_color(s.value)
            active = v == current
            done = _is_done(v, current)
            with ui.element("div").classes("flex flex-col items-center gap-0.5"):
                if active:
                    ui.element("div").classes("w-3 h-3 rounded-full border-2").style(
                        f"background:{color};border-color:{color};box-shadow:0 0 6px {color}"
                    )
                elif done:
                    ui.element("div").classes("w-3 h-3 rounded-full").style(
                        "background:var(--text-nav-primary)"
                    )
                else:
                    ui.element("div").classes("w-3 h-3 rounded-full border").style(
                        "border-color:var(--fg-tertiary)"
                    )
                label = t(f"status.{v}")
                c = "var(--text-nav-primary)" if active or done else "var(--fg-tertiary)"
                ui.label(label).classes("text-[10px] font-medium whitespace-nowrap").style(
                    f"color:{c}"
                )
            if i < len(STAGES) - 1:
                line_color = (
                    "var(--text-nav-primary)"
                    if _is_done(STAGES[i + 1].value, current)
                    else "var(--fg-tertiary)"
                )
                ui.element("div").style(
                    f"width:24px;height:1px;background:{line_color};margin-bottom:14px"
                )


def _library_btn(project_id: str) -> None:
    async def _open() -> None:
        from ..exploring.literature_library import LiteratureLibrary

        repo = get_current_user_repo()
        project = await repo.get(project_id)
        papers = []
        if project and project.exploring_state:
            papers = project.exploring_state.get("papers", [])
        lib = LiteratureLibrary(papers)
        dlg = await lib.build()
        dlg.open()

    ui.button(icon="library_books", on_click=_open).props("flat round dense").tooltip(
        t("exploring.library")
    )


def _build_footer(project_id: str, state: dict[str, Any], checklist: Checklist, chat: Any) -> None:
    with ui.element("div").classes(
        "flex items-center justify-between px-5 py-3 border-t ts-border-divider"
    ):
        with ui.element("div").classes("flex items-center gap-3"):

            async def _save() -> None:
                if chat._msgs:
                    state["messages"] = [
                        {"role": m["role"], "content": m["content"], "agent": m.get("agent", "")}
                        for m in chat._msgs
                    ]
                await _save_session(project_id, dict(state))

            ui.button(t("designing.save"), on_click=lambda: asyncio.ensure_future(_save())).classes(
                "ts-btn-secondary"
            ).props("no-caps")

        with ui.element("div").classes("flex items-center gap-3"):
            if checklist.all_completed:
                ui.label(t("designing.ready")).classes("text-xs").style("color:#16a34a")

            async def _confirm() -> None:
                if not checklist.all_completed:
                    ui.notify(t("designing.incomplete"), type="warning")
                    return
                confirm_btn.props("loading")
                confirm_btn.disable()
                try:
                    await _do_confirm()
                finally:
                    confirm_btn.props(remove="loading")
                    confirm_btn.enable()

            async def _do_confirm() -> None:
                # Sync chat messages to state before confirming
                if chat._msgs:
                    state["messages"] = [
                        {"role": m["role"], "content": m["content"], "agent": m.get("agent", "")}
                        for m in chat._msgs
                    ]
                # Granularity check: must pass before entering RESEARCHING
                outline_md = state.get("outline", "")
                if outline_md:
                    try:
                        llm = await get_llm_for_agent("reviewer")
                        report = await check_outline_granularity(outline_md, llm)
                        if not report.all_pass:
                            failed = [s for s in report.sections if s.level != "just_right"]
                            msg = "粒度校验不通过:\n" + "\n".join(
                                f"  - {s.heading}: {s.level} ({s.reason})" for s in failed
                            )
                            ui.notify(msg, type="warning", position="center", timeout=8000)
                            return
                    except Exception as e:
                        ui.notify(f"粒度校验失败: {e}", type="warning")
                        return
                await _save_session(project_id, dict(state))
                repo = get_current_user_repo()
                project = await repo.get(project_id)
                if project:
                    project.status = ProjectStatus.RESEARCHING
                    await repo.update(project)
                    ui.notify(t("designing.confirmed"), type="positive")

            confirm_btn = ui.button(t("designing.confirm"), on_click=_confirm).classes("ts-btn-primary").props(
                "no-caps"
            )


async def _save_session(project_id: str, state: dict[str, Any]) -> None:
    try:
        repo = get_current_user_repo()
        project = await repo.get(project_id)
        if project is None:
            return
        outline_md = state.get("outline", "")
        merged = {**project.exploring_state}
        merged["outline"] = outline_md
        merged["template"] = state.get("template", "imrad")
        merged["messages"] = state.get("messages", [])
        project.exploring_state = merged
        # Also save outline markdown to file for next phase
        from pathlib import Path

        data_dir = (
            Path(__file__).parent.parent.parent.parent.parent.parent
            / "data"
            / "projects"
            / project_id
        )
        data_dir.mkdir(parents=True, exist_ok=True)
        (data_dir / "outline.md").write_text(outline_md, encoding="utf-8")
        await repo.update(project)
    except Exception as e:
        import logging

        logging.getLogger(__name__).error("Failed to save session for %s: %s", project_id, e)
        ui.notify(f"????: {e}", type="negative", timeout=3000)


def _not_found() -> None:
    with ui.element("div").classes("flex items-center justify-center h-full"):
        ui.label(t("exploring.not_found")).classes("ts-text-secondary text-lg")


def _theme_toggle_button() -> None:
    with (
        ui.element("button")
        .classes(
            "ts-btn-tertiary inline-flex items-center justify-center"
            " rounded-full cursor-pointer h-[38px] w-[38px] px-0 gap-0"
        )
        .props("id=ts-theme-toggle")
    ):
        ui.timer(0.3, lambda: ui.run_javascript(_THEME_JS), once=True)
        with ui.element("span").props("id=ts-icon-sun"):
            ui.html(_SUN_ICON)
        with ui.element("span").props("id=ts-icon-moon").style("display:none"):
            ui.html(_MOON_ICON)


def _lang_btn() -> None:
    lang = get_lang()
    label = "ZH" if lang == "zh" else "EN"
    btn = ui.element("button").classes(
        "ts-btn-tertiary inline-flex items-center justify-center"
        " rounded-full cursor-pointer h-[38px] px-3 text-sm font-medium"
    )

    def _switch(_: object) -> None:
        toggle_lang()
        ui.navigate.reload()

    btn.on("click", _switch)
    with btn:
        ui.label(label).classes("ts-lang-label")
