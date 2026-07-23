"""ThesisOS 启动入口。"""

import uvicorn

from thesisos.config import get_settings
from thesisos.presentation.api import create_app

app = create_app()

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )
