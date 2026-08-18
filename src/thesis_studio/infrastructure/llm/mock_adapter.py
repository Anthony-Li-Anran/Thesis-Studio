"""Mock LLM provider for graceful degradation when no API key is configured."""

from __future__ import annotations


class MockLLMProvider:
    """Fallback LLM provider that returns placeholder responses.

    Used when OPENAI_API_KEY or other provider credentials are not configured.
    Allows the UI to render without crashing while clearly indicating
    that LLM features are unavailable.
    """

    async def generate(
        self,
        prompt: str,
        *,
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> str:
        return "[Mock] LLM not configured. Set OPENAI_API_KEY in .env."

    async def generate_stream(
        self,
        prompt: str,
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> str:
        return "[Mock] LLM not configured. Set OPENAI_API_KEY in .env."
