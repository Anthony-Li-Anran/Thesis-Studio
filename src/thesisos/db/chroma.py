"""ChromaDB 向量数据库客户端。"""

import threading
from typing import Any

from ..config import get_settings
from ..core.logging import get_logger

logger = get_logger(__name__)

_client: Any = None
_lock = threading.Lock()


def get_chroma_client() -> Any:
    """获取 ChromaDB 客户端单例（线程安全）。"""
    global _client
    if _client is None:
        with _lock:
            if _client is None:
                import chromadb

                settings = get_settings()
                settings.chroma_path.parent.mkdir(parents=True, exist_ok=True)
                _client = chromadb.PersistentClient(
                    path=str(settings.chroma_path),
                )
                logger.info("ChromaDB 客户端已初始化: %s", settings.chroma_path)
    return _client
