"""Ollama 本地模型提供商。"""

import httpx

from ..core.exceptions import LLMUnavailableError
from ..core.logging import get_logger

logger = get_logger(__name__)


class OllamaProvider:
    """Ollama 本地模型提供商。"""

    def __init__(self, url: str, model: str) -> None:
        self._url = url.rstrip("/")
        self._model = model

    async def generate(
        self,
        prompt: str,
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> str:
        """调用 Ollama API 生成文本。"""
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(
                    f"{self._url}/api/generate",
                    json={
                        "model": self._model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": temperature},
                    },
                )
                resp.raise_for_status()
                return str(resp.json()["response"])
        except httpx.ConnectError:
            raise LLMUnavailableError(f"无法连接 Ollama: {self._url}，请确认已启动") from None
