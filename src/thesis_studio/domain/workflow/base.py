"""工作流阶段接口与上下文。"""

from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class WorkflowContext:
    """工作流上下文，在阶段间传递数据。"""

    project_id: str
    data: dict[str, object] = field(default_factory=dict)


@dataclass
class StepResult:
    """单个工作流阶段的执行结果。"""

    step_name: str
    success: bool
    output: dict[str, object] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


class WorkflowStep(Protocol):
    """工作流阶段接口。每个阶段实现 execute 方法。"""

    name: str

    async def execute(self, ctx: WorkflowContext) -> StepResult: ...
