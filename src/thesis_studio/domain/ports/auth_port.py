"""认证端口：领域层定义、基础设施层实现。"""

from typing import Protocol, runtime_checkable

from ..models.user import User


@runtime_checkable
class AuthProvider(Protocol):
    """认证提供者协议，注册/登录/游客三入口。"""

    async def register(self, email: str, password: str, name: str = "") -> User:
        """注册新用户，返回 User；冲突抛 AuthConflictError。"""
        ...

    async def login(self, email: str, password: str) -> User:
        """登录，返回 User；失败抛 AuthCredentialError。"""
        ...

    async def get_by_id(self, user_id: str) -> User | None:
        """按 ID 查询用户。"""
        ...

    def create_guest(self) -> User:
        """创建游客会话。"""
        ...
