"""Agent protocol and sandbox configuration."""

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, Field


class SandboxConfig(BaseModel):
    """Per-agent sandbox constraint.

    Limits what an agent can access: paths, APIs, and resources.
    """

    allowed_paths: list[str] = Field(default_factory=list)
    allowed_apis: list[str] = Field(default_factory=list)
    timeout_seconds: int = 300
    max_memory_mb: int = 1024


@runtime_checkable
class AgentProtocol(Protocol):
    """Agent interface. Every agent must implement handle()."""

    name: str
    sandbox: SandboxConfig

    async def handle(self, message: str, context: dict) -> str:
        """Process a message and return a response."""
        ...


@dataclass
class AgentMessage:
    """A single message in the agent conversation."""

    role: str  # "user" | "agent" | "system"
    content: str
    agent_name: str = ""
    metadata: dict = field(default_factory=dict)
