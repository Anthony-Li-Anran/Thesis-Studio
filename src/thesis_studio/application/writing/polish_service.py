"""文本润色服务：提升学术文本的规范性和可读性。"""

from ...domain.ports.llm_port import LLMProvider


class TextPolisher:
    """学术文本润色服务。"""

    def __init__(self, llm: LLMProvider) -> None:
        self._llm = llm

    async def polish_text(self, text: str) -> str:
        """润色学术文本。"""
        prompt = f"""你是一位学术写作编辑。请润色以下文本，提升其学术性和可读性，
保持原意不变，修正语法和表达问题：

{text}

请直接返回润色后的文本："""
        return await self._llm.generate(prompt, temperature=0.3)
