"""Researcher agent implementation — LangGraph-powered with Skills."""

from __future__ import annotations

from typing import Any

from ...domain.agent.base import SandboxConfig
from ...domain.ports.llm_port import LLMProvider
from ...domain.workflow import NodeContext, ProgressCallback, run_exploring
from ..logging import get_logger
from ..sandbox import Sandbox
from ..skill import AcademicSearchSkill, ClusterSkill, PaperParserSkill, ReviewGenSkill

logger = get_logger(__name__)


class ResearcherImpl:
    """Researcher agent: step-by-step conversational pipeline via LangGraph."""

    name = "researcher"
    sandbox = SandboxConfig(
        allowed_apis=[
            "https://api.semanticscholar.org",
            "http://export.arxiv.org",
            "http://localhost:11434",
            "https://api.openai.com",
        ],
        timeout_seconds=300,
    )

    def __init__(self, llm: LLMProvider) -> None:
        self._llm = llm
        self._sandbox = Sandbox(self.sandbox)
        self._search_skill = AcademicSearchSkill()
        self._parser_skill = PaperParserSkill()
        self._cluster_skill = ClusterSkill(llm)
        self._review_skill = ReviewGenSkill(llm)
        self._ctx = NodeContext(
            llm=self._llm,
            search_skill=self._search_skill,
            parser_skill=self._parser_skill,
            cluster_skill=self._cluster_skill,
            review_skill=self._review_skill,
        )
        self._persisted_state: dict[str, Any] = {}

    def set_progress_callback(self, callback: ProgressCallback | None) -> None:
        """Set or clear the progress callback for streaming UI updates."""
        self._ctx.progress_callback = callback

    async def handle(self, message: str, context: dict[str, Any]) -> dict[str, Any]:
        """Process user message via LangGraph and return enriched state."""
        history = context.get("history", [])
        topic = context.get("topic", message)
        lang = context.get("lang", "en")
        self._ctx.lang = lang

        try:
            result = await run_exploring(
                ctx=self._ctx,
                message=message,
                history=history,
                existing_state=self._persisted_state,
            )
            self._persisted_state = {
                "papers": result.get("papers", []),
                "clusters": result.get("clusters", []),
                "review": result.get("review", {}),
                "html_content": result.get("html_content", ""),
                "topic": result.get("topic", topic),
            }
            return {
                "response": result.get("response", ""),
                "review": result.get("review", {}),
                "clusters": result.get("clusters", []),
                "papers": result.get("papers", []),
                "html_content": result.get("html_content", ""),
                "suggestions": result.get("suggestions", []),
                "error": result.get("error", ""),
                "intent": result.get("intent", ""),
                "topic": result.get("topic", topic),
            }
        except Exception:
            logger.exception("Researcher graph error")
            return {
                "response": "Something went wrong. Please try again.",
                "error": "graph execution failed",
                "review": {},
                "clusters": [],
                "papers": [],
                "html_content": "",
                "suggestions": [],
                "intent": "",
                "topic": topic,
            }

    def update_llm(self, llm: LLMProvider) -> None:
        self._llm = llm
        self._ctx.llm = llm
        self._cluster_skill._llm = llm
        self._review_skill._llm = llm

    def reset_state(self) -> None:
        self._persisted_state = {}
