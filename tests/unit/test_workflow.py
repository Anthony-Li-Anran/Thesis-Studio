"""工作流模块测试。"""

from thesis_studio.domain.workflow import StepResult, WorkflowContext


def test_workflow_context_default_data() -> None:
    """WorkflowContext 默认 data 应为空字典。"""
    ctx = WorkflowContext(project_id="test")
    assert ctx.data == {}


def test_step_result_fields() -> None:
    """StepResult 应正确存储字段。"""
    result = StepResult(step_name="test", success=True)
    assert result.step_name == "test"
    assert result.success is True
    assert result.output == {}
    assert result.errors == []
