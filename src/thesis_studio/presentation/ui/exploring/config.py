"""Shared constants for EXPLORING phase."""

from thesis_studio.domain.models.project import STATUS_FLOW

AGENT_COLORS: dict[str, str] = {
    "researcher": "#2563eb",
    "executor": "#ea580c",
    "writer": "#16a34a",
    "reviewer": "#db2777",
    "debater": "#7c3aed",
}

AGENT_LABELS: dict[str, str] = {
    "researcher": "Researcher",
    "executor": "Executor",
    "writer": "Writer",
    "reviewer": "Reviewer",
    "debater": "Debater",
}

STAGES = STATUS_FLOW
