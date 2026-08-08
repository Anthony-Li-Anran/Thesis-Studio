"""Ollama 本地模型适配器。实现 LLMProvider 端口。"""

import httpx

from ...domain.exceptions import LLMUnavailableError
from ..logging import get_logger

logger = get_logger(__name__)


class OllamaAdapter:
    """Ollama 本地模型适配器。"""

    def __init__(self, url: str, model: str, timeout: float = 120.0) -> None:
        self._url = url.rstrip("/")
        self._model = model
        self._timeout = timeout

    async def generate(
        self,
        prompt: str,
        *,
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> str:
        """调用 Ollama API 生成文本。"""
        options: dict[str, object] = {"temperature": temperature}
        if max_tokens is not None:
            options["num_predict"] = max_tokens

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.post(
                    f"{self._url}/api/generate",
                    json={
                        "model": self._model,
                        "prompt": prompt,
                        "stream": False,
                        "options": options,
                    },
                )
                resp.raise_for_status()
                return str(resp.json()["response"])
        except httpx.ConnectError:
            raise LLMUnavailableError(f"无法连接 Ollama: {self._url}，请确认已启动") from None
        except httpx.HTTPStatusError as e:
            logger.error("Ollama HTTP 错误: %s", e)
            raise LLMUnavailableError(f"Ollama 返回错误: {e.response.status_code}") from e

    async def generate_stream(
        self,
        prompt: str,
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> str:
        """流式生成（当前实现为收集后返回，后续可改为真流式）。"""
        return await self.generate(prompt, temperature=temperature, max_tokens=max_tokens)
