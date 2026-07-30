"""FastAPI REST API 接口。"""

from .app import create_app
from .dependencies import get_services

__all__ = ["create_app", "get_services"]
