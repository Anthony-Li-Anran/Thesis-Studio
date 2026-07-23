"""OpenAI 云端模型提供商。"""

import httpx

from ..core.logging import get_logger

logger = get_logger(__name__)


class OpenAIProvider:
    """OpenAI API 提供商。"""

    def __init__(self, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model = model
        self._url = "https://api.openai.com/v1/chat/completions"

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

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(self._url, headers=headers, json=body)
            resp.raise_for_status()
            return str(resp.json()["choices"][0]["message"]["content"])
