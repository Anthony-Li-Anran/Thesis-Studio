"""DESIGNING phase skill implementations — LLM-driven research design skills."""

from __future__ import annotations

import json
import re
from typing import Any

from ...domain.ports.llm_port import LLMProvider
from ...domain.skill.base import Skill, SkillConfig, SkillResult
from ...domain.skill.designing import (
    AlternativeInput,
    AlternativeOutput,
    AssumptionChallengeInput,
    AssumptionChallengeOutput,
    CompletenessInput,
    CompletenessOutput,
    DataAnalysisInput,
    DataAnalysisOutput,
    FormatComplianceInput,
    FormatComplianceOutput,
    LogicChainInput,
    LogicChainOutput,
    MethodologyInput,
    MethodologyOutput,
    ResearchQuestionInput,
    ResearchQuestionOutput,
    RiskInput,
    RiskOutput,
    TheoryFrameworkInput,
    TheoryFrameworkOutput,
)
from ..logging import get_logger

logger = get_logger(__name__)


class ResearchDesignSkill(Skill):
    """Researcher skill: design RQs, methodology, theory framework, data analysis."""

    config: SkillConfig = SkillConfig(name="research_design")

    def __init__(self, llm: LLMProvider) -> None:
        super().__init__()
        self._llm = llm

    async def execute(self, **kwargs: Any) -> SkillResult:
        mode = kwargs.get("mode", "question")
        try:
            if mode == "question":
                result = await self._design_questions(**kwargs)
            elif mode == "methodology":
                result = await self._design_methodology(**kwargs)
            elif mode == "theory":
                result = await self._build_theory(**kwargs)
            elif mode == "analysis":
                result = await self._plan_analysis(**kwargs)
            else:
                return SkillResult(success=False, error=f"Unknown mode: {mode}")
            return SkillResult(success=True, data=result.model_dump() if result else {})
        except Exception as e:
            logger.error("ResearchDesignSkill failed: %s", e)
            return SkillResult(success=False, error=str(e))

    async def _design_questions(self, **kwargs: Any) -> ResearchQuestionOutput:
        inp = ResearchQuestionInput(**kwargs)
        prompt = (
            f"You are a senior researcher. Given this research gap:\n{inp.gap}\n"
            f"Domain: {inp.domain}\n"
            f"Design 3-5 precise, testable research questions. "
            f"For each question, explain why it is scientifically valuable.\n\n"
            f"Return JSON:\n"
            f'{{"questions": ["RQ1", "RQ2", ...], "rationale": "why these are good questions"}}'
        )
        response = await self._llm.generate(prompt, temperature=0.5)
        return self._parse_json(response, ResearchQuestionOutput)

    async def _design_methodology(self, **kwargs: Any) -> MethodologyOutput:
        inp = MethodologyInput(**kwargs)
        qs = "\n".join(f"- {q}" for q in inp.questions)
        prompt = (
            f"Research questions:\n{qs}\nDomain: {inp.domain}\nConstraints: {inp.constraints}\n\n"
            f"Design a complete methodology. Include: paradigm (qualitative/quantitative/mixed), "
            f"research design, variables, sample/data source, procedure, and analysis methods.\n\n"
            f"Return JSON:\n"
            f'{{"paradigm": "...", "design": "...", "variables": "...", '
            f'"sample": "...", "procedure": "...", "analysis": "..."}}'
        )
        response = await self._llm.generate(prompt, temperature=0.5)
        return self._parse_json(response, MethodologyOutput)

    async def _build_theory(self, **kwargs: Any) -> TheoryFrameworkOutput:
        inp = TheoryFrameworkInput(**kwargs)
        concepts = "\n".join(inp.key_concepts)
        prompt = (
            f"Topic: {inp.topic}\nKey concepts:\n{concepts}\n\n"
            f"Build a theoretical framework. Define each concept, describe the framework, "
            f"and explain relationships between concepts.\n\n"
            f"Return JSON:\n"
            f'{{"concepts": ["definition of concept 1", ...], '
            f'"framework": "framework description", '
            f'"relationships": ["concept A -> concept B: relationship type"]}}'
        )
        response = await self._llm.generate(prompt, temperature=0.5)
        return self._parse_json(response, TheoryFrameworkOutput)

    async def _plan_analysis(self, **kwargs: Any) -> DataAnalysisOutput:
        inp = DataAnalysisInput(**kwargs)
        prompt = (
            f"Methodology: {inp.methodology}\nVariables: {inp.variables}\n\n"
            f"Plan the data analysis: list statistical/analytical methods, "
            f"expected results, and recommended tools/software.\n\n"
            f"Return JSON:\n"
            f'{{"methods": ["method 1", "method 2"], "expected": "expected results", "tools": "recommended tools"}}'
        )
        response = await self._llm.generate(prompt, temperature=0.5)
        return self._parse_json(response, DataAnalysisOutput)

    @staticmethod
    def _parse_json(response: str, model_cls: type) -> Any:
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            return model_cls(**json.loads(json_match.group()))
        return model_cls()


class CritiqueSkill(Skill):
    """Debater skill: challenge assumptions, analyze alternatives, spot risks."""

    config: SkillConfig = SkillConfig(name="critique")

    def __init__(self, llm: LLMProvider) -> None:
        super().__init__()
        self._llm = llm

    async def execute(self, **kwargs: Any) -> SkillResult:
        mode = kwargs.get("mode", "assumption")
        try:
            if mode == "assumption":
                result = await self._challenge(**kwargs)
            elif mode == "alternative":
                result = await self._alternatives(**kwargs)
            elif mode == "risk":
                result = await self._risks(**kwargs)
            else:
                return SkillResult(success=False, error=f"Unknown mode: {mode}")
            return SkillResult(success=True, data=result.model_dump() if result else {})
        except Exception as e:
            logger.error("CritiqueSkill failed: %s", e)
            return SkillResult(success=False, error=str(e))

    async def _challenge(self, **kwargs: Any) -> AssumptionChallengeOutput:
        inp = AssumptionChallengeInput(**kwargs)
        prompt = (
            f"Critically examine this statement:\n{inp.statement}\nContext: {inp.context}\n\n"
            f"Identify hidden assumptions, challenge each one, and propose alternatives.\n\n"
            f"Return JSON:\n"
            f'{{"assumptions": ["hidden assumption 1", ...], '
            f'"challenges": ["challenge 1", ...], '
            f'"alternatives": ["alternative approach 1", ...]}}'
        )
        response = await self._llm.generate(prompt, temperature=0.7)
        return _parse_json(response, AssumptionChallengeOutput)

    async def _alternatives(self, **kwargs: Any) -> AlternativeOutput:
        inp = AlternativeInput(**kwargs)
        prompt = (
            f"Current method: {inp.current_method}\nGoal: {inp.goal}\nContext: {inp.context}\n\n"
            f"Propose 2-3 alternative methods. For each, describe pros and cons. "
            f"Give a final recommendation.\n\n"
            f"Return JSON:\n"
            f'{{"alternatives": [{{"name": "...", "pros": "...", "cons": "..."}}], '
            f'"recommendation": "..."}}'
        )
        response = await self._llm.generate(prompt, temperature=0.7)
        return _parse_json(response, AlternativeOutput)

    async def _risks(self, **kwargs: Any) -> RiskOutput:
        inp = RiskInput(**kwargs)
        prompt = (
            f"Plan: {inp.plan}\nContext: {inp.context}\n\n"
            f"Identify potential risks in this research plan. "
            f"For each risk, assess severity and propose mitigation.\n\n"
            f"Return JSON:\n"
            f'{{"risks": [{{"risk": "...", "severity": "high/medium/low", "mitigation": "..."}}], '
            f'"overall": "overall risk assessment"}}'
        )
        response = await self._llm.generate(prompt, temperature=0.7)
        return _parse_json(response, RiskOutput)


class ReviewSkill(Skill):
    """Reviewer skill: check completeness, validate logic, ensure format compliance."""

    config: SkillConfig = SkillConfig(name="review")

    def __init__(self, llm: LLMProvider) -> None:
        super().__init__()
        self._llm = llm

    async def execute(self, **kwargs: Any) -> SkillResult:
        mode = kwargs.get("mode", "completeness")
        try:
            if mode == "completeness":
                result = await self._check_completeness(**kwargs)
            elif mode == "logic":
                result = await self._validate_logic(**kwargs)
            elif mode == "format":
                result = await self._check_format(**kwargs)
            else:
                return SkillResult(success=False, error=f"Unknown mode: {mode}")
            return SkillResult(success=True, data=result.model_dump() if result else {})
        except Exception as e:
            logger.error("ReviewSkill failed: %s", e)
            return SkillResult(success=False, error=str(e))

    async def _check_completeness(self, **kwargs: Any) -> CompletenessOutput:
        inp = CompletenessInput(**kwargs)
        prompt = (
            f"Review this outline for completeness:\n```\n{inp.outline}\n```\n"
            f"Template: {inp.template}\n\n"
            f"List missing sections, weak sections, and give a 0-100 completeness score.\n\n"
            f"Return JSON:\n"
            f'{{"missing": ["missing section 1", ...], "weak": ["weak section 1", ...], "score": 80}}'
        )
        response = await self._llm.generate(prompt, temperature=0.3)
        return _parse_json(response, CompletenessOutput)

    async def _validate_logic(self, **kwargs: Any) -> LogicChainOutput:
        inp = LogicChainInput(**kwargs)
        prompt = (
            f"Validate the logic chain of this outline:\n```\n{inp.outline}\n```\n\n"
            f"Check the flow: RQ -> methods -> expected results -> discussion -> conclusion. "
            f"Find logical gaps, contradictions, and suggest fixes.\n\n"
            f"Return JSON:\n"
            f'{{"issues": ["issue 1", ...], "suggestions": ["suggestion 1", ...]}}'
        )
        response = await self._llm.generate(prompt, temperature=0.3)
        return _parse_json(response, LogicChainOutput)

    async def _check_format(self, **kwargs: Any) -> FormatComplianceOutput:
        inp = FormatComplianceInput(**kwargs)
        prompt = (
            f"Check format compliance:\nOutline:\n```\n{inp.outline}\n```\n"
            f"Rules: {inp.rules}\n\n"
            f"List violations and suggest fixes.\n\n"
            f"Return JSON:\n"
            f'{{"violations": ["violation 1", ...], "fixed": ["already compliant item 1", ...]}}'
        )
        response = await self._llm.generate(prompt, temperature=0.3)
        return _parse_json(response, FormatComplianceOutput)


def _parse_json(response: str, model_cls: type) -> Any:
    # Try ```json block first
    json_match = re.search(r"```json\s*(.*?)\s*```", response, re.DOTALL)
    if json_match:
        try:
            return model_cls(**json.loads(json_match.group(1)))
        except (json.JSONDecodeError, TypeError):
            pass
    # Try to find the first balanced JSON object
    depth = 0
    start = -1
    for i, ch in enumerate(response):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start >= 0:
                try:
                    return model_cls(**json.loads(response[start : i + 1]))
                except (json.JSONDecodeError, TypeError):
                    start = -1
    return model_cls()
