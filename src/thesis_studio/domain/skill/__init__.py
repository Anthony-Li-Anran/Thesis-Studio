"""Skill domain module."""

from .base import Skill, SkillConfig, SkillResult
from .interfaces import (
    AcademicSearchInput,
    AcademicSearchOutput,
    ClusterInput,
    ClusterOutput,
    PaperParserInput,
    PaperParserOutput,
    ReviewGenInput,
    ReviewGenOutput,
    SearchQuery,
)

__all__ = [
    "AcademicSearchInput",
    "AcademicSearchOutput",
    "ClusterInput",
    "ClusterOutput",
    "PaperParserInput",
    "PaperParserOutput",
    "ReviewGenInput",
    "ReviewGenOutput",
    "SearchQuery",
    "Skill",
    "SkillConfig",
    "SkillResult",
]
