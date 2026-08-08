"""EXPLORING phase state — TypedDict, intent model, and NodeContext."""

from __future__ import annotations

import re
from collections.abc import Awaitable, Callable
from typing import Annotated, Any, Literal, TypedDict

from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

from ..ports.llm_port import LLMProvider

ProgressCallback = Callable[[dict[str, Any]], Awaitable[None]]


class IntentResult(BaseModel):
    """LLM intent classification result."""

    intent: Literal[
        "search",
        "cluster",
        "review",
        "final_report",
        "explain",
        "compare",
        "chat",
    ] = Field(description="Classified user intent")
    thinking: str = Field(default="", description="Brief reasoning")
    topic: str = Field(
        default="",
        description="The research topic to search for, extracted from the message",
    )
    params: dict[str, Any] = Field(default_factory=dict)


class Suggestion(BaseModel):
    """A suggested next action for the user."""

    label: str = Field(description="Button label shown to user")
    action_text: str = Field(
        description="Text sent as user message when clicked"
    )


class ExploringState(TypedDict, total=False):
    """Shared state for the EXPLORING workflow graph."""

    messages: Annotated[list[dict[str, str]], add_messages]
    current_message: str
    topic: str
    intent: str
    intent_params: dict[str, Any]
    search_queries: list[dict[str, Any]]
    raw_papers: list[dict[str, Any]]
    papers: list[dict[str, Any]]
    clusters: list[dict[str, Any]]
    review: dict[str, Any]
    html_content: str
    response: str
    suggestions: list[dict[str, str]]
    lang: str
    error: str


INTENT_PROMPT = """\
You are a research intent classifier for Thesis Studio, an academic literature exploration system.
Your job is to understand what the user wants and route them to the right workflow step.

CONTEXT:
Conversation history:
{history}

Current session: {paper_count} papers loaded, {cluster_count} clusters, review exists: {has_review}.
Existing research topic: "{existing_topic}"

USER MESSAGE: "{message}"

TASK: Classify the user intent and extract the research topic.

OUTPUT FORMAT: Return ONLY valid JSON, no other text:
{{
  "intent": "<one of: search|cluster|review|final_report|explain|compare|chat>",
  "thinking": "<1 sentence reasoning>",
  "topic": "<English academic keywords, 3-8 words, or empty>",
  "params": {{}}
}}

INTENT DEFINITIONS:
- search: User wants to discover papers on a topic. Extract the topic.
  Examples: "find papers on attention" → "attention mechanisms"
            "I'm interested in transformer efficiency" → "transformer efficiency"
- cluster: User wants to group existing papers by theme. No topic needed.
- review: User wants to generate a literature review from clusters. No topic needed.
- final_report: User wants to generate/download the final HTML report. No topic needed.
- explain: User wants explanation of a specific paper. params: {{"paper_index": 0}}
- compare: User wants to compare papers. params: {{"paper_indices": [0, 1]}}
- chat: Casual conversation, greetings, questions about capabilities. No topic needed.

TOPIC EXTRACTION RULES:
- You MUST extract the core research concept, not the full sentence.
- You MUST use English academic terms for the topic.
- You MUST keep the topic between 3 and 8 words.
- If the user refers to the existing topic (e.g., "continue", "go deeper"), reuse it.
- If the user is just chatting, you MUST leave topic as an empty string.
- Do NOT invent topics that are not in the user's message.

Please do your best, this is important for accurate research workflow routing."""


async def classify_intent(
    state: ExploringState, llm: LLMProvider
) -> IntentResult:
    """Classify user intent via LLM; falls back to safe defaults."""
    messages = state.get("messages", [])
    history_parts = []
    for m in messages[-6:]:
        if hasattr(m, 'type'):
            role = m.type
            content = getattr(m, 'content', '') or ''
        elif isinstance(m, dict):
            role = m.get('role', '')
            content = m.get('content', '')
        else:
            continue
        history_parts.append(f"- {role}: {content[:200]}")
    history = "\n".join(history_parts)
    papers = state.get("papers", [])
    clusters = state.get("clusters", [])
    review = state.get("review", {})
    existing_topic = state.get("topic", "")

    prompt = INTENT_PROMPT.format(
        history=history or "(none)",
        message=state["current_message"],
        paper_count=len(papers),
        cluster_count=len(clusters),
        has_review=bool(review),
        existing_topic=existing_topic or "(none)",
    )
    try:
        resp = await llm.generate(prompt, system="You are a research intent classifier. Always respond with valid JSON only.", temperature=0.2, max_tokens=400)
        json_match = re.search(r"\{.*\}", resp, re.DOTALL)
        if json_match:
            return IntentResult.model_validate_json(json_match.group())
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("Intent classification failed: %s", e)
    return IntentResult(
        intent="chat", thinking="llm_unavailable_fallback"
    )


class NodeContext:
    """Holds skill instances and LLM reference for graph nodes.

    Kept outside the state because state must be JSON-serialisable.
    """

    def __init__(
        self,
        llm: LLMProvider,
        search_skill: Any,
        parser_skill: Any,
        cluster_skill: Any,
        review_skill: Any,
        lang: str = "en",
        progress_callback: ProgressCallback | None = None,
    ) -> None:
        self.llm = llm
        self.search_skill = search_skill
        self.parser_skill = parser_skill
        self.cluster_skill = cluster_skill
        self.review_skill = review_skill
        self.lang = lang
        self.progress_callback = progress_callback

    async def emit(self, event: dict[str, Any]) -> None:
        """Emit a progress event to the callback if set."""
        if self.progress_callback is not None:
            await self.progress_callback(event)
