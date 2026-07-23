"""工作流引擎（兼容保留）。工作流定义保留在此，编排逻辑在 application 层。"""

from .base import StepResult, WorkflowContext, WorkflowStep

__all__ = ["WorkflowStep", "WorkflowContext", "StepResult"]
