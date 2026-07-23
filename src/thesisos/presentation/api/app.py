"""FastAPI 应用工厂。"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ... import __version__
from ...domain.exceptions import (
    LLMRateLimitError,
    LLMUnavailableError,
    ThesisOSError,
    ValidationError,
)
from .routes import router


def create_app() -> FastAPI:
    """创建并配置 FastAPI 应用实例。"""
    app = FastAPI(
        title="ThesisOS",
        version=__version__,
        description="面向毕业论文生成的 AI 研究助手",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(router)

    # 异常处理器：根据异常类型返回不同状态码
    @app.exception_handler(ThesisOSError)
    async def handle_thesisos_error(request: Request, exc: ThesisOSError) -> JSONResponse:
        status_map: dict[type[ThesisOSError], int] = {
            LLMUnavailableError: 503,
            LLMRateLimitError: 429,
            ValidationError: 422,
        }
        status_code = 400
        for exc_type, code in status_map.items():
            if isinstance(exc, exc_type):
                status_code = code
                break
        return JSONResponse(status_code=status_code, content={"detail": str(exc)})

    return app
