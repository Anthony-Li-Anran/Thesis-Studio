"""Skill protocol — Pydantic-based, framework-agnostic."""

from collections.abc import AsyncIterator
from typing import Any

from pydantic import BaseModel


class SkillConfig(BaseModel):
    """Base configuration for a skill."""

    name: str
    description: str = ""
    timeout_seconds: int = 60


class SkillResult(BaseModel):
    """Result from a skill execution."""

    success: bool
    data: dict[str, Any] = {}
    error: str = ""


class Skill(BaseModel):
    """Skill interface. Each skill is a Pydantic model with config and execute."""

    config: SkillConfig

    async def execute(self, **kwargs: Any) -> SkillResult:
        """Execute the skill with given parameters."""
        raise NotImplementedError

    async def execute_stream(self, **kwargs: Any) -> AsyncIterator[str]:
        """Execute with streaming output. Default wraps execute()."""
        result = await self.execute(**kwargs)
        yield result.model_dump_json()
        if False:  # make this a generator
            yield ""
