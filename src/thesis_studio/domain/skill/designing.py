"""DESIGNING phase skill interfaces — Pydantic data models for skill I/O."""

from __future__ import annotations

from pydantic import BaseModel, Field


# ── Researcher skills ──

class ResearchQuestionInput(BaseModel):
    gap: str = Field(description="研究空白描述")
    domain: str = Field(description="研究领域/学科")
    context: str = Field(default="", description="额外上下文")

class ResearchQuestionOutput(BaseModel):
    questions: list[str] = Field(default_factory=list, description="提炼的研究问题")
    rationale: str = Field(default="", description="为什么这些问题是好的")

class MethodologyInput(BaseModel):
    questions: list[str] = Field(default_factory=list, description="研究问题")
    domain: str = Field(description="学科")
    constraints: str = Field(default="", description="资源约束")

class MethodologyOutput(BaseModel):
    paradigm: str = Field(default="", description="研究范式(定性/定量/混合)")
    design: str = Field(default="", description="研究设计描述")
    variables: str = Field(default="", description="变量定义")
    sample: str = Field(default="", description="样本/数据来源")
    procedure: str = Field(default="", description="实验/调查流程")
    analysis: str = Field(default="", description="分析方法")

class TheoryFrameworkInput(BaseModel):
    topic: str = Field(description="研究主题")
    key_concepts: list[str] = Field(default_factory=list)
    papers: list[dict] = Field(default_factory=list, description="文献库论文")

class TheoryFrameworkOutput(BaseModel):
    concepts: list[str] = Field(default_factory=list, description="核心概念定义")
    framework: str = Field(default="", description="理论框架描述")
    relationships: list[str] = Field(default_factory=list, description="概念间关系")

class DataAnalysisInput(BaseModel):
    methodology: str = Field(description="方法描述")
    variables: str = Field(default="")

class DataAnalysisOutput(BaseModel):
    methods: list[str] = Field(default_factory=list, description="统计/分析方法")
    expected: str = Field(default="", description="预期结果")
    tools: str = Field(default="", description="推荐工具/软件")


# ── Debater skills ──

class AssumptionChallengeInput(BaseModel):
    statement: str = Field(description="需要质疑的陈述")
    context: str = Field(default="")

class AssumptionChallengeOutput(BaseModel):
    assumptions: list[str] = Field(default_factory=list, description="隐含假设")
    challenges: list[str] = Field(default_factory=list, description="质疑点")
    alternatives: list[str] = Field(default_factory=list, description="替代方案")

class AlternativeInput(BaseModel):
    current_method: str = Field(description="当前方法")
    goal: str = Field(description="研究目标")
    context: str = Field(default="")

class AlternativeOutput(BaseModel):
    alternatives: list[dict[str, str]] = Field(default_factory=list, description="[{name, pros, cons}]")
    recommendation: str = Field(default="")

class RiskInput(BaseModel):
    plan: str = Field(description="方案描述")
    context: str = Field(default="")

class RiskOutput(BaseModel):
    risks: list[dict[str, str]] = Field(default_factory=list, description="[{risk, severity, mitigation}]")
    overall: str = Field(default="", description="总体风险评估")


# ── Reviewer skills ──

class CompletenessInput(BaseModel):
    outline: str = Field(description="大纲 Markdown")
    template: str = Field(default="imrad", description="格式模板")

class CompletenessOutput(BaseModel):
    missing: list[str] = Field(default_factory=list, description="缺失章节")
    weak: list[str] = Field(default_factory=list, description="薄弱章节")
    score: float = Field(default=0.0, description="完成度评分 0-100")

class LogicChainInput(BaseModel):
    outline: str = Field(description="大纲 Markdown")

class LogicChainOutput(BaseModel):
    issues: list[str] = Field(default_factory=list, description="逻辑问题")
    suggestions: list[str] = Field(default_factory=list, description="修改建议")

class FormatComplianceInput(BaseModel):
    outline: str = Field(description="大纲 Markdown")
    rules: str = Field(description="格式规则 JSON 或描述")

class FormatComplianceOutput(BaseModel):
    violations: list[str] = Field(default_factory=list, description="违规项")
    fixed: list[str] = Field(default_factory=list, description="已修正项")
