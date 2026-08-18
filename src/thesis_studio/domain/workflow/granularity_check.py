"""Outline granularity checker — ensures sections describe "what to study", not "how to study".

The check classifies each section heading into three levels:
- too_coarse: generic labels like "研究方法", "实验设计" — no research direction specified
- just_right: specific research direction, e.g. "Softmax Kernel with Random Fourier Features"
- too_fine: implementation details, e.g. "用PyTorch实现RFF在ImageNet上验证"
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from ..ports.llm_port import LLMProvider


class SectionGranularity(BaseModel):
    """Verdict for a single section heading."""

    heading: str = Field(description="The original section heading text")
    level: Literal["too_coarse", "just_right", "too_fine"] = Field(
        description="Granularity classification"
    )
    reason: str = Field(description="One-sentence explanation in Chinese")


class GranularityReport(BaseModel):
    """Full granularity check report for the entire outline."""

    sections: list[SectionGranularity] = Field(default_factory=list)
    all_pass: bool = Field(default=False)
    summary: str = Field(default="", description="Overall assessment in Chinese")


GRANULARITY_PROMPT = """\
You are an academic thesis outline reviewer. Your job is to check whether each section heading
in a thesis outline is at the correct granularity level.

THE RULE:
Each section heading must describe WHAT to study, but NOT HOW to study it.
- Too COARSE: generic labels that don't reveal the specific research direction
- JUST RIGHT: specific research direction, but no implementation details
- Too FINE: contains implementation details (tools, datasets, parameters, steps)

EXAMPLES:

| Heading | Level | Why |
|---------|-------|-----|
| 3.1 研究方法 | too_coarse | Just says "methods", doesn't say what direction |
| 3.1 Softmax Kernel with Random Fourier Features | just_right | Specific theory direction |
| 3.1 用PyTorch实现RFF注意力机制 | too_fine | Includes tool (PyTorch) and implementation verb |
| 4.1 实验设计 | too_coarse | Just says "experiment design", no what |
| 4.1 Long Sequence Classification | just_right | Specific experiment type |
| 4.1 在Long-Range Arena上测试，batch_size=32 | too_fine | Includes dataset and hyperparameter |
| 2.1 文献综述 | too_coarse | Generic label |
| 2.1 Transformer Efficiency: A Survey | just_right | Specific review topic |
| 3.3 数据收集 | too_coarse | Generic label |
| 3.3 中文医疗文本语料库构建 | just_right | Specific data direction |
| 3.5 数据分析 | too_coarse | Generic label |
| 3.5 多变量回归分析 | just_right | Specific analysis method, no tools |
| 3.5 用SPSS做独立样本t检验 | too_fine | Includes tool name |

TASK:
Analyze each section heading in the outline below. Output a JSON object with:
- "sections": array of {heading, level, reason} for each heading
- "all_pass": true only if ALL sections are "just_right"
- "summary": one-sentence overall verdict in Chinese

OUTLINE TO REVIEW:
{outline_sections}

OUTPUT FORMAT: Return ONLY valid JSON, no other text:
{{
  "sections": [
    {{"heading": "1.2 研究问题", "level": "just_right", "reason": "..."}},
    ...
  ],
  "all_pass": true,
  "summary": "所有章节粒度合格"
}}
"""


async def check_outline_granularity(
    outline_md: str,
    llm: LLMProvider,
) -> GranularityReport:
    """Check whether every section heading in the outline is at the right granularity.

    Returns a GranularityReport with per-section verdicts and an overall pass/fail.
    """
    import re

    # Extract all ## and ### headings from the outline
    headings: list[str] = []
    for line in outline_md.splitlines():
        stripped = line.strip()
        if stripped.startswith("### ") or stripped.startswith("## "):
            # Remove the markdown markers for cleaner display
            clean = re.sub(r"^#+\s*", "", stripped)
            headings.append(clean)

    if not headings:
        return GranularityReport(
            sections=[], all_pass=False, summary="大纲中没有找到任何章节标题"
        )

    sections_text = "\n".join(f"- {h}" for h in headings)
    prompt = GRANULARITY_PROMPT.format(outline_sections=sections_text)

    try:
        import json as _json
        resp = await llm.generate(
            prompt,
            system="You are a precise academic outline reviewer. Always respond with valid JSON.",
            temperature=0.1,
            max_tokens=2000,
        )
        json_match = re.search(r"\{.*\}", resp, re.DOTALL)
        if json_match:
            data = _json.loads(json_match.group())
            report = GranularityReport(
                sections=[SectionGranularity(**s) for s in data.get("sections", [])],
                all_pass=data.get("all_pass", False),
                summary=data.get("summary", ""),
            )
            return report
    except Exception:
        pass

    return GranularityReport(
        sections=[], all_pass=False, summary="粒度校验失败：无法解析 LLM 响应"
    )
