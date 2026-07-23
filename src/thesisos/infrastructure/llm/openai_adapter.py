"""OpenAI 云端模型适配器。实现 LLMProvider 端口。"""

import httpx

from ...core.logging import get_logger
from ...domain.exceptions import LLMError, LLMRateLimitError, LLMTokenLimitError

logger = get_logger(__name__)


class OpenAIAdapter:
    """OpenAI API 适配器。"""

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str = "https://api.openai.com/v1",
        timeout: float = 120.0,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    async def generate(
        self,
        prompt: str,
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> str:
        """调用 OpenAI API 生成文本。"""
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        body: dict[str, object] = {
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }
        if max_tokens is not None:
            body["max_tokens"] = max_tokens

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.post(
                    f"{self._base_url}/chat/completions",
                    headers=headers,
                    json=body,
                )
                resp.raise_for_status()
                data = resp.json()
                return str(data["choices"][0]["message"]["content"])
        except httpx.ConnectError as e:
            raise LLMError("无法连接 OpenAI API") from e
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            if status == 429:
                raise LLMRateLimitError("OpenAI API 速率限制，请稍后重试") from e
            if status == 400 and "token" in str(e.response.text).lower():
                raise LLMTokenLimitError("Token 超限，请缩短输入") from e
            logger.error("OpenAI HTTP %d 错误: %s", status, e)
            raise LLMError(f"OpenAI API 返回错误 {status}") from e

    async def generate_stream(
        self,
        prompt: str,
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> str:
        """流式生成（当前实现为收集后返回）。"""
        return await self.generate(prompt, temperature=temperature, max_tokens=max_tokens)
