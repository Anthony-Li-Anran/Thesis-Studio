"""LLM 模块（兼容重导出）。适配器已迁移至 infrastructure.llm，端口在 domain.ports。"""

from ..domain.ports.llm_port import LLMProvider
from ..infrastructure.llm.factory import LLMFactory

create_llm = LLMFactory().create  # 兼容旧接口

__all__ = ["LLMProvider", "LLMFactory", "create_llm"]
