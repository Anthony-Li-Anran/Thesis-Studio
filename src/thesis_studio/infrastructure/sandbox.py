"""Sandbox implementation — path and API access control."""

import asyncio
import os
from pathlib import Path

from thesis_studio.domain.agent.base import SandboxConfig
from thesis_studio.domain.exceptions import ThesisStudioError


class SandboxError(ThesisStudioError):
    """Sandbox access violation."""


class Sandbox:
    """Enforces SandboxConfig constraints on agent operations."""

    def __init__(self, config: SandboxConfig) -> None:
        self._config = config

    def check_path(self, path: str | Path) -> Path:
        """Verify a path is within allowed paths. Raises SandboxError."""
        resolved = Path(path).resolve()
        for allowed in self._config.allowed_paths:
            allowed_resolved = Path(allowed).resolve()
            try:
                resolved.relative_to(allowed_resolved)
                return resolved
            except ValueError:
                continue
        raise SandboxError(f"路径访问被拒绝: {path}")

    def check_api(self, url: str) -> str:
        """Verify an API URL is in the allowed list. Raises SandboxError."""
        for allowed in self._config.allowed_apis:
            if allowed in url or url.startswith(allowed):
                return url
        raise SandboxError(f"API 访问被拒绝: {url}")

    async def run_with_timeout(self, coro, timeout: int | None = None) -> object:
        """Run a coroutine with timeout. Raises SandboxError on timeout."""
        t = timeout or self._config.timeout_seconds
        try:
            return await asyncio.wait_for(coro, timeout=t)
        except TimeoutError as err:
            raise SandboxError(f"操作超时 ({t}s)") from err

    @staticmethod
    def for_researcher() -> "Sandbox":
        """Create a sandbox for the Researcher agent."""
        return Sandbox(
            SandboxConfig(
                allowed_paths=[str(Path.cwd()), os.environ.get("TMP", "/tmp")],
                allowed_apis=[
                    "https://api.semanticscholar.org",
                    "https://export.arxiv.org",
                    "http://localhost:11434",
                    "https://api.openai.com",
                ],
                timeout_seconds=300,
                max_memory_mb=2048,
            )
        )
