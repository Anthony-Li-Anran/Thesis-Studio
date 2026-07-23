"""FastAPI 应用工厂（兼容重导出）。已迁移至 presentation.api。"""

from ..presentation.api.app import create_app

__all__ = ["create_app"]
