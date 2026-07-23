"""嵌入模型（兼容重导出）。端口已迁移至 domain.ports，适配器在 infrastructure.embedding。"""

from ..domain.ports.embedding_port import EmbeddingProvider

__all__ = ["EmbeddingProvider"]
