"""Agent service — message routing and streaming bridge."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from typing import Any

from ...domain.agent.base import AgentMessage
from ...domain.ports.llm_port import LLMProvider
from ...domain.ports.repository_port import PaperRepository
from ...infrastructure.agent import ResearcherImpl
from ...infrastructure.logging import get_logger

logger = get_logger(__name__)


class AgentService:
    """Routes messages to agents and bridges streaming output to frontend."""

    def __init__(self, llm: LLMProvider, paper_repo: PaperRepository | None = None) -> None:
        self._llm = llm
        self._paper_repo = paper_repo
        self._researcher = ResearcherImpl(llm, paper_repo)

    async def _refresh_llm(self) -> None:
        """Re-resolve LLM from settings card so config changes take effect."""
        from ...infrastructure.bootstrap import get_llm_for_agent
        try:
            new_llm = await get_llm_for_agent("researcher")
            self._llm = new_llm
            self._researcher.update_llm(new_llm)
        except Exception as e:
            logger.warning("Failed to refresh LLM from settings: %s", e)

    async def send_message(
        self,
        content: str,
        agent_name: str = "researcher",
        context: dict[str, Any] | None = None,
    ) -> AgentMessage:
        """Send a message to an agent and get a response."""
        await self._refresh_llm()
        ctx = context or {}
        agent = self._resolve_agent(agent_name)
        result = await agent.handle(content, ctx)
        response_text = result.get("response", "")
        ctx["review"] = result.get("review", {})
        ctx["clusters"] = result.get("clusters", [])
        ctx["papers"] = result.get("papers", [])
        ctx["topic"] = result.get("topic", "")
        metadata: dict[str, Any] = {
            "html_content": result.get("html_content", ""),
            "topic": result.get("topic", ""),
            "intent": result.get("intent", ""),
            "suggestions": result.get("suggestions", []),
        }
        return AgentMessage(
            role="agent",
            content=response_text,
            agent_name=agent_name,
            metadata=metadata,
        )

    async def stream_message(
        self,
        content: str,
        agent_name: str = "researcher",
        context: dict[str, Any] | None = None,
    ) -> AsyncIterator[str]:
        """Stream agent progress and response as SSE events."""
        await self._refresh_llm()
        ctx = context or {}
        agent = self._resolve_agent(agent_name)

        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()

        async def on_progress(event: dict[str, Any]) -> None:
            await queue.put(event)

        agent.set_progress_callback(on_progress)

        async def run() -> None:
            try:
                result = await agent.handle(content, ctx)
                await queue.put({"type": "_result", "data": result})
            except Exception as e:
                logger.exception("Agent stream error")
                await queue.put({"type": "error", "content": str(e)})

        task = asyncio.create_task(run())

        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=0.15)
            except TimeoutError:
                if task.done():
                    exc = task.exception()
                    if exc:
                        yield json.dumps({"type": "error", "content": str(exc)})
                    # Drain any remaining events before breaking
                    while not queue.empty():
                        try:
                            leftover = queue.get_nowait()
                            if leftover["type"] == "_result":
                                result = leftover["data"]
                                response_text = result.get("response", "")
                                suggestions = result.get("suggestions", [])
                                html_content = result.get("html_content", "")
                                if response_text:
                                    yield json.dumps({
                                        "type": "message",
                                        "content": response_text,
                                        "agent": agent_name,
                                        "suggestions": suggestions,
                                    })
                                if html_content:
                                    yield json.dumps({
                                        "type": "review",
                                        "html_content": html_content,
                                        "topic": result.get("topic", ""),
                                    })
                                clusters = result.get("clusters", [])
                                papers = result.get("papers", [])
                                if clusters:
                                    yield json.dumps({
                                        "type": "graph",
                                        "clusters": clusters,
                                        "papers": papers,
                                    })
                            elif leftover["type"] == "error":
                                yield json.dumps(leftover)
                            else:
                                yield json.dumps(leftover)
                        except Exception:
                            pass
                    break
                continue

            if event["type"] == "_result":
                result = event["data"]
                response_text = result.get("response", "")
                suggestions = result.get("suggestions", [])
                html_content = result.get("html_content", "")
                if response_text:
                    yield json.dumps({
                        "type": "message",
                        "content": response_text,
                        "agent": agent_name,
                        "suggestions": suggestions,
                    })
                if html_content:
                    yield json.dumps({
                        "type": "review",
                        "html_content": html_content,
                        "topic": result.get("topic", ""),
                    })
                clusters = result.get("clusters", [])
                papers = result.get("papers", [])
                if clusters:
                    yield json.dumps({
                        "type": "graph",
                        "clusters": clusters,
                        "papers": papers,
                    })
                break
            elif event["type"] == "error":
                yield json.dumps(event)
                break
            else:
                yield json.dumps(event)

        agent.set_progress_callback(None)
        yield json.dumps({"type": "done"})

    async def run_explore_pipeline(
        self,
        topic: str,
        context: dict[str, Any] | None = None,
    ) -> AsyncIterator[str]:
        """Run the full EXPLORING pipeline with streaming progress."""
        await self._refresh_llm()
        ctx = context or {"topic": topic}
        agent = self._researcher

        yield json.dumps({"type": "progress", "stage": "start", "content": "Analyzing intent..."})
        try:
            result = await agent.handle(topic, ctx)
            response_text = result.get("response", "")
            suggestions = result.get("suggestions", [])
            html_content = result.get("html_content", "")
            yield json.dumps({
                "type": "message",
                "content": response_text,
                "agent": "researcher",
                "suggestions": suggestions,
            })
            if html_content:
                yield json.dumps({
                    "type": "review",
                    "html_content": html_content,
                })
            clusters = result.get("clusters", [])
            papers = result.get("papers", [])
            if clusters:
                yield json.dumps({
                    "type": "graph",
                    "clusters": clusters,
                    "papers": papers,
                })
        except Exception as e:
            logger.error("Pipeline error: %s", e)
            yield json.dumps({"type": "error", "content": str(e)})
        yield json.dumps({"type": "done"})

    def get_session_data(self) -> dict[str, Any]:
        """Return accumulated session state for persistence."""
        return self._researcher.get_persisted_state()

    def reset_session(self) -> None:
        """Reset the session state."""
        self._researcher.reset_state()

    def _resolve_agent(self, name: str) -> ResearcherImpl:
        if name == "researcher":
            return self._researcher
        raise ValueError(f"Unknown agent: {name}")
