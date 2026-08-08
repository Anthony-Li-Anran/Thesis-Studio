"""EXPLORING phase page: chat room + knowledge graph + detail panel."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from tempfile import gettempdir
from typing import Any

from nicegui import ui

from ....application.exploring.agent_service import AgentService
from ....domain.models.project import ProjectStatus
from ....infrastructure.bootstrap import get_current_user_repo, get_llm_for_agent
from ..i18n import get_lang, t, toggle_lang
from ..theme import apply_theme, logo
from .chat_room import ChatRoom
from .stage_progress import stage_progress

_CHEVRON_LEFT = (
    '<svg fill="currentColor" width="16" height="16" viewBox="0 0 20 20"'
    ' xmlns="http://www.w3.org/2000/svg"><path d="M12.4707 15.2792C12.7304'
    " 15.5389 12.7304 15.9609 12.4707 16.2206C12.211 16.4803 11.789 16.4803"
    " 11.5293 16.2206L5.7793 10.4706L5.69434 10.3661C5.52383 10.108 5.55103"
    " 9.75655 5.7793 9.52929L11.5293 3.77929L11.6338 3.69433C11.8919 3.52482"
    " 12.2434 3.55202 12.4707 3.77929C12.698 4.00656 12.7282 4.35807 12.5577"
    ' 4.6162L12.4727 4.7207L7.19141 10L12.4707 15.2792Z"></path></svg>'
)  # noqa: E501

_SUN_ICON = (
    '<svg fill="currentColor" width="16" height="16" viewBox="0 0 20 20" '
    'xmlns="http://www.w3.org/2000/svg" aria-hidden="true" class="shrink-0">'
    '<path d="M10 3.5C10.3452 3.5 10.625 3.77982 10.625 4.125V5.375C10.625'
    ' 5.72018 10.3452 6 10 6C9.65482 6 9.375 5.72018 9.375 5.375V4.125C9.375'
    ' 3.77982 9.65482 3.5 10 3.5ZM10 14C10.3452 14 10.625 14.2798 10.625'
    ' 14.625V15.875C10.625 16.2202 10.3452 16.5 10 16.5C9.65482 16.5 9.375'
    ' 16.2202 9.375 15.875V14.625C9.375 14.2798 9.65482 14 10 14ZM10 7C8.34315'
    ' 7 7 8.34315 7 10C7 11.6569 8.34315 13 10 13C11.6569 13 13 11.6569 13'
    ' 10C13 8.34315 11.6569 7 10 7ZM4.125 10.625C3.77982 10.625 3.5 10.3452'
    ' 3.5 10C3.5 9.65482 3.77982 9.375 4.125 9.375H5.375C5.72018 9.375 6'
    ' 9.65482 6 10C6 10.3452 5.72018 10.625 5.375 10.625H4.125ZM14.625'
    ' 10.625C14.2798 10.625 14 10.3452 14 10C14 9.65482 14.2798 9.375 14.625'
    ' 9.375H15.875C16.2202 9.375 16.5 9.65482 16.5 10C16.5 10.3452 16.2202'
    ' 10.625 15.875 10.625H14.625ZM5.75736 5.75736C6.00144 5.51328 6.00144'
    ' 5.11655 5.75736 4.87247C5.51328 4.62839 5.11655 4.62839 4.87247'
    ' 4.87247L3.98871 5.75623C3.74463 6.00031 3.74463 6.39704 3.98871'
    ' 6.64112C4.23279 6.8852 4.62952 6.8852 4.8736 6.64112L5.75736'
    ' 5.75736ZM15.1275 13.3589C15.3716 13.1148 15.7683 13.1148 16.0124'
    ' 13.3589L16.8962 14.2426C17.1403 14.4867 17.1403 14.8834 16.8962'
    ' 15.1275C16.6521 15.3716 16.2554 15.3716 16.0113 15.1275L15.1275'
    ' 14.2438C14.8834 13.9997 14.8834 13.603 15.1275 13.3589ZM14.2426'
    ' 5.75736C14.4867 5.51328 14.8834 5.51328 15.1275 5.75736L16.0113'
    ' 6.64112C16.2554 6.8852 16.2554 7.28193 16.0113 7.52601C15.7672'
    ' 7.77009 15.3705 7.77009 15.1264 7.52601L14.2426 6.64225C13.9985'
    ' 6.39817 13.9985 6.00144 14.2426 5.75736ZM4.87247 15.1275C4.62839'
    ' 14.8835 4.62839 14.4867 4.87247 14.2426L5.75623 13.3589C6.00031'
    ' 13.1148 6.39704 13.1148 6.64112 13.3589C6.8852 13.603 6.8852'
    ' 13.9997 6.64112 14.2438L5.75736 15.1275C5.51328 15.3716 5.11655'
    ' 15.3716 4.87247 15.1275Z"></path></svg>'
)  # noqa: E501

_MOON_ICON = (
    '<svg fill="currentColor" width="16" height="16" viewBox="0 0 20 20" '
    'xmlns="http://www.w3.org/2000/svg" aria-hidden="true" class="shrink-0">'
    '<path d="M16.3589 13.1055C15.941 14.257 15.2225 15.2741 14.283'
    ' 16.044C13.3436 16.814 12.2194 17.309 11.0068 17.475C9.79422 17.641'
    ' 8.54114 17.4715 7.39942 16.9851C6.2577 16.4986 5.27144 15.7131'
    ' 4.54975 14.7135C3.82806 13.7139 3.39793 12.5378 3.30399 11.3111'
    'C3.21004 10.0845 3.45572 8.85373 4.01463 7.75141C4.57355 6.64909'
    ' 5.42482 5.71714 6.48069 5.05547C7.53657 4.3938 8.75782 4.02693'
    ' 10.0105 3.99348C10.3141 3.98614 10.618 4.02782 10.9122 4.11776'
    'C10.3708 4.99472 10.0872 6.00763 10.0938 7.04024C10.1004 8.07285'
    ' 10.397 9.08236 10.9498 9.95296C11.5026 10.8236 12.2891 11.5201'
    ' 13.22 11.9648C14.151 12.4095 15.189 12.5844 16.2136 12.4694C16.3198'
    ' 12.4574 16.425 12.439 16.5288 12.4143C16.4749 12.6478 16.406 12.8772'
    ' 16.3224 13.1013L16.3589 13.1055Z"></path></svg>'
)  # noqa: E501

_THEME_JS = """\
<script>
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
tsTryInitTheme();
</script>"""

_CLUSTER_COLORS = [
    "#5470c6", "#91cc75", "#fac858", "#ee6666", "#73c0de",
    "#3ba272", "#fc8452", "#9a60b4", "#ea7ccc",
]


async def _get_agent_service() -> AgentService:
    llm = await get_llm_for_agent("researcher")
    return AgentService(llm)


@ui.page("/project/{project_id}/exploring", title="Thesis Studio")  # type: ignore[untyped-decorator]
def exploring_page(project_id: str) -> None:
    """EXPLORING phase page entry."""
    apply_theme()
    ui.add_body_html(_THEME_JS)
    ui.timer(0, lambda: _build_page(project_id), once=True)


async def _build_page(project_id: str) -> None:
    project = await get_current_user_repo().get(project_id)
    if project is None:
        _not_found()
        return
    state: dict[str, str] = {"html": "", "topic": ""}
    graph_container: list[ui.element | None] = [None]

    def _on_review(topic: str, html_content: str) -> None:
        state["html"] = html_content
        state["topic"] = topic

    def _on_graph(
        clusters: list[dict[str, Any]], papers: list[dict[str, Any]]
    ) -> None:
        gc = graph_container[0]
        if gc is None:
            return
        gc.clear()
        with gc:
            _render_graph(clusters, papers)

    # Root: fixed to viewport, no page scroll
    with ui.element("div").style(
        "position:fixed;top:0;left:0;right:0;bottom:0;"
        "display:flex;flex-direction:column;overflow:hidden"
    ):
        _build_header()
        with ui.element("div").style(
            "flex:1;min-height:0;display:flex;overflow:hidden"
        ):
            with ui.element("div").classes(
                "w-[45%] border-r ts-border-divider"
            ).style("display:flex;flex-direction:column;min-height:0"):
                _build_chat_panel(project_id, _on_review, _on_graph)
            with ui.element("div").classes("w-[55%]").style(
                "display:flex;flex-direction:column;min-height:0"
            ):
                graph_container[0] = _build_graph_panel()
        _build_footer(state)


def _not_found() -> None:
    with ui.element("div").classes(
        "flex items-center justify-center h-full"
    ):
        ui.label(t("exploring.not_found")).classes(
            "ts-text-secondary text-lg"
        )


def _build_header() -> None:
    with ui.element("div").classes(
        "flex items-center justify-between px-5 py-3"
        " border-b ts-border-divider"
    ):
        with ui.element("div").classes("flex items-center gap-3"):
            with ui.link(target="/").classes(
                "ts-btn-tertiary inline-flex items-center justify-center"
                " rounded-full h-[38px] w-[38px]"
            ):
                ui.html(_CHEVRON_LEFT)
            logo()
        with ui.element("div").classes("flex-1 flex justify-center"):
            stage_progress(ProjectStatus.EXPLORING.value)
        with ui.element("div").classes("flex items-center gap-2"):
            _theme_toggle_button()
            _lang_btn()


def _build_chat_panel(
    project_id: str, on_review: Any, on_graph: Any
) -> None:
    with ui.element("div").style(
        "display:flex;flex-direction:column;height:100%;min-height:0"
    ):
        with ui.element("div").classes(
            "px-4 py-3 border-b ts-border-divider"
        ):
            ui.label(t("exploring.title")).classes(
                "text-sm font-medium ts-text-nav"
            )
        wrapper = ui.element("div").style(
            "flex:1;min-height:0;overflow:hidden"
        )

        async def _init_chat() -> None:
            svc = await _get_agent_service()
            chat = ChatRoom()
            chat.agent_service = svc
            chat.project_id = project_id
            chat.on_review(on_review)
            chat.on_graph(on_graph)
            with wrapper:
                chat.build()
            chat.add_message(
                "researcher", t("exploring.welcome"), "researcher"
            )

        ui.timer(0, _init_chat, once=True)


def _build_graph_panel() -> ui.element:
    with ui.element("div").style(
        "display:flex;flex-direction:column;height:100%;min-height:0"
    ):
        with ui.element("div").classes(
            "px-4 py-3 border-b ts-border-divider"
        ):
            ui.label(t("exploring.graph")).classes(
                "text-sm font-medium ts-text-nav"
            )
        chart_area = ui.element("div").classes("p-4").style(
            "flex:1;min-height:0;overflow:hidden"
        )
        with chart_area:
            with ui.element("div").classes(
                "ts-bg-sidepanel rounded-2xl p-6 h-full"
                " flex items-center justify-center"
            ):
                with ui.element("div").classes("text-center"):
                    ui.label(
                        t("exploring.graph_placeholder")
                    ).classes("ts-text-nav text-lg font-medium mb-2")
                    ui.label(t("exploring.graph_hint")).classes(
                        "ts-text-nav-secondary text-sm"
                    )
    return chart_area


def _render_graph(
    clusters: list[dict[str, Any]], papers: list[dict[str, Any]]
) -> None:
    """Render ECharts force-directed knowledge graph."""
    cluster_nodes = []
    paper_nodes = []
    links = []

    for ci, c in enumerate(clusters):
        color = _CLUSTER_COLORS[ci % len(_CLUSTER_COLORS)]
        theme = c.get("theme", f"Cluster {ci + 1}")
        cluster_papers = c.get("papers", [])
        desc = c.get("description", "")

        cluster_nodes.append({
            "name": theme,
            "symbolSize": max(30, 20 + len(cluster_papers) * 2),
            "category": ci,
            "itemStyle": {"color": color},
            "label": {
                "show": True, "fontSize": 13, "fontWeight": "bold"
            },
            "tooltip": {
                "formatter": (
                    f"<b>{theme}</b><br/>"
                    f"{desc}<br/>"
                    f"{len(cluster_papers)} papers"
                ),
            },
        })

        for p in cluster_papers:
            pid = p.get("paper_id", "")
            title = (p.get("title", "") or "Untitled")[:60]
            year = p.get("year", "")
            authors = p.get("authors", [])
            author_str = ", ".join(authors[:3]) if authors else ""

            paper_nodes.append({
                "name": f"p_{pid}",
                "symbolSize": 12,
                "category": ci,
                "itemStyle": {"color": color, "opacity": 0.7},
                "label": {"show": False},
                "tooltip": {
                    "formatter": (
                        f"<b>{title}</b><br/>"
                        f"{author_str}<br/>"
                        f"{year}"
                    ),
                },
                "title": title,
                "year": year,
                "authors": author_str,
            })

            links.append({
                "source": theme,
                "target": f"p_{pid}",
                "lineStyle": {
                    "color": color, "opacity": 0.3, "width": 1
                },
            })

    for ci, c in enumerate(clusters):
        cluster_papers = c.get("papers", [])
        for i in range(len(cluster_papers)):
            for j in range(i + 1, min(i + 4, len(cluster_papers))):
                pid_i = cluster_papers[i].get("paper_id", "")
                pid_j = cluster_papers[j].get("paper_id", "")
                if pid_i and pid_j:
                    links.append({
                        "source": f"p_{pid_i}",
                        "target": f"p_{pid_j}",
                        "lineStyle": {
                            "color": _CLUSTER_COLORS[
                                ci % len(_CLUSTER_COLORS)
                            ],
                            "opacity": 0.15,
                            "width": 0.5,
                        },
                    })

    categories = [
        {"name": c.get("theme", f"Cluster {i + 1}")}
        for i, c in enumerate(clusters)
    ]

    option = {
        "tooltip": {"trigger": "item", "textStyle": {"fontSize": 12}},
        "legend": {
            "data": [c.get("theme", "") for c in clusters],
            "orient": "vertical",
            "left": 10,
            "top": 10,
            "textStyle": {"fontSize": 11, "color": "#888"},
        },
        "series": [{
            "type": "graph",
            "layout": "force",
            "categories": categories,
            "nodes": cluster_nodes + paper_nodes,
            "links": links,
            "roam": True,
            "draggable": True,
            "force": {
                "gravity": 0.15,
                "repulsion": 300,
                "edgeLength": [80, 200],
            },
            "emphasis": {
                "focus": "adjacency",
                "lineStyle": {"width": 3},
            },
            "lineStyle": {"color": "source", "curveness": 0.2},
        }],
    }

    ui.echart(option).classes("w-full h-full")


def _build_footer(state: dict[str, str]) -> None:
    with ui.element("div").classes(
        "flex items-center justify-between px-5 py-3"
        " border-t ts-border-divider"
    ):
        def _view_review() -> None:
            if not state["html"]:
                ui.notify(
                    t("exploring.no_review_yet"), type="warning"
                )
                return
            # Sanitize filename: topic_Literature_Review_time
            raw_topic = (state["topic"] or "review").split("\n")[0].strip()
            safe = "".join(c for c in raw_topic if c.isascii() and (c.isalnum() or c in "_-"))
            safe = safe.strip("_-")[:50] or "review"
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"{safe}-Literature_Review-{ts}.html"
            path = Path(gettempdir()) / name
            path.write_text(state["html"], encoding="utf-8")
            ui.download(str(path))

        ui.button(
            t("exploring.review_btn"), on_click=_view_review
        ).classes("ts-btn-secondary").props("no-caps")
        with ui.element("div").classes("flex items-center gap-2"):

            def _download() -> None:
                if not state["html"]:
                    ui.notify(
                        t("exploring.no_review_yet"), type="warning"
                    )
                    return
                raw_topic = (state["topic"] or "review").split("\n")[0].strip()
                safe = "".join(c for c in raw_topic if c.isascii() and (c.isalnum() or c in "_-"))
                safe = safe.strip("_-")[:50] or "review"
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                name = f"{safe}-Literature_Review-{ts}.html"
                path = Path(gettempdir()) / name
                path.write_text(state["html"], encoding="utf-8")
                ui.download(str(path))

            ui.button(
                t("exploring.download_html"), on_click=_download
            ).classes("ts-btn-secondary").props("no-caps")
            ui.button(t("exploring.confirm_btn")).classes(
                "ts-btn-primary"
            ).props("no-caps")


def _theme_toggle_button() -> None:
    with ui.element("button").classes(
        "ts-btn-tertiary inline-flex items-center justify-center"
        " rounded-full cursor-pointer h-[38px] w-[38px] px-0 gap-0"
    ).props("id=ts-theme-toggle"):
        with ui.element("span").props("id=ts-icon-sun"):
            ui.html(_SUN_ICON)
        with ui.element("span").props("id=ts-icon-moon").style(
            "display:none"
        ):
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
