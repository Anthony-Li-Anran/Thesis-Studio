"""API 路由定义。"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    """健康检查。"""
    return {"status": "ok"}
