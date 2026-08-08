"""OpenAI 云端模型适配器。实现 LLMProvider 端口。"""

import httpx

from ...domain.exceptions import LLMError, LLMRateLimitError, LLMTokenLimitError
from ..logging import get_logger

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
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> str:
        """调用 OpenAI API 生成文本。"""
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        body: dict[str, object] = {
            "model": self._model,
            "messages": messages,
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
            resp_body = e.response.text[:500] if e.response.text else ""
            logger.error("OpenAI HTTP %d: %s", status, resp_body)
            raise LLMError(f"OpenAI API {status}: {resp_body[:200]}") from e

    async def generate_stream(
        self,
        prompt: str,
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> str:
        """流式生成（当前实现为收集后返回）。"""
        return await self.generate(prompt, temperature=temperature, max_tokens=max_tokens)
