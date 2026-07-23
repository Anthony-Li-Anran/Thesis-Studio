"""数据分析用例。"""

from ...domain.ports.llm_port import LLMProvider


class AnalysisService:
    """数据分析用例：数据理解、统计分析、可视化建议。"""

    def __init__(self, llm: LLMProvider) -> None:
        self._llm = llm

    async def analyze_data_description(self, data_summary: str) -> str:
        """基于数据摘要生成分析建议。"""
        prompt = f"""你是一位数据分析专家。请基于以下数据描述，提供分析建议：

数据描述：
{data_summary}

请提供：
1. 适合的统计分析方法
2. 建议的可视化图表类型
3. 可能的研究发现方向

用中文回答："""
        return await self._llm.generate(prompt, temperature=0.3)

    async def interpret_results(self, results: str) -> str:
        """解释分析结果。"""
        prompt = f"""你是一位学术研究专家。请解释以下数据分析结果的意义：

分析结果：
{results}

请用学术语言解释这些结果的含义、局限性和对研究问题的启示。用中文回答："""
        return await self._llm.generate(prompt, temperature=0.4)
