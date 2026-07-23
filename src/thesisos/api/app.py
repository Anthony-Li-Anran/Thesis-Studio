"""FastAPI 应用工厂。"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from ..core.exceptions import ThesisOSError


def create_app() -> FastAPI:
    """创建并配置 FastAPI 应用实例。"""
    app = FastAPI(title="ThesisOS", version="0.1.0")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.exception_handler(ThesisOSError)
    async def handle_error(request: Request, exc: ThesisOSError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    return app
