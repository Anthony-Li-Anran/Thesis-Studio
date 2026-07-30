"""Thesis Studio 启动入口。"""

import uvicorn

from thesis_studio.config import get_settings
from thesis_studio.presentation.api import create_app

app = create_app()

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )
