"""ECharts force-directed knowledge graph for paper clustering."""

from nicegui import ui

_GRAPH_JS = """
export default {
  tooltip: {},
  series: [{
    type: 'graph',
    layout: 'force',
    force: { repulsion: 200, edgeLength: 150 },
    roam: true,
    draggable: true,
    data: [],
    links: [],
    lineStyle: { color: 'var(--fg-tertiary)', curveness: 0.2 },
    label: { show: true, fontSize: 10, color: 'var(--text-nav-secondary)' },
  }]
}
"""


def knowledge_graph() -> ui.echart:
    """Render an interactive knowledge graph."""
    return ui.echart(
        {},
    ).classes("w-full h-full").style("min-height:400px")


def update_graph(
    chart: ui.echart,
    nodes: list[dict[str, str]],
    edges: list[dict[str, str]],
) -> None:
    """Update graph data."""
    option = {
        "tooltip": {"trigger": "item", "formatter": "{b}"},
        "series": [{
            "type": "graph",
            "layout": "force",
            "force": {"repulsion": 200, "edgeLength": 150},
            "roam": True,
            "draggable": True,
            "data": [
                {
                    "name": n["name"],
                    "symbolSize": n.get("size", 14),
                    "itemStyle": {"color": n.get("color", "#3b82f6")},
                    "id": n.get("id", ""),
                }
                for n in nodes
            ],
            "links": [
                {
                    "source": e["source"],
                    "target": e["target"],
                    "lineStyle": {
                        "type": e.get("line_type", "solid"),
                        "color": "var(--fg-tertiary)",
                    },
                }
                for e in edges
            ],
            "label": {
                "show": True,
                "fontSize": 10,
                "color": "var(--text-nav-secondary)",
                "formatter": "{b}",
            },
            "lineStyle": {"color": "var(--fg-tertiary)", "curveness": 0.2},
            "emphasis": {"focus": "adjacency", "lineStyle": {"width": 3}},
        }],
    }
    chart._props["options"] = option
    chart.update()
