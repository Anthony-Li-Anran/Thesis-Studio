"""本地认证提供者：SQLite 持久化 + PBKDF2 密码哈希。"""

import hashlib
import secrets
from collections.abc import Callable
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.exceptions import AuthConflictError, AuthCredentialError
from ...domain.models.user import User
from ..db.sqlite import UserModel, get_session_factory
from ..logging import get_logger

logger = get_logger(__name__)

SessionFactory = Callable[[], AsyncSession]

_ITERATIONS = 100_000


def _hash_password(password: str, salt: str | None = None) -> str:
    """PBKDF2-SHA256 哈希，返回 salt:hash 串。"""
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), _ITERATIONS)
    return f"{salt}:{digest.hex()}"


def _verify_password(password: str, stored: str) -> bool:
    """恒定时间比较，防时序攻击。"""
    if ":" not in stored:
        return False
    salt, expected = stored.split(":", 1)
    actual = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), _ITERATIONS
    ).hex()
    return secrets.compare_digest(actual, expected)


class LocalAuthProvider:
    """基于 SQLite 的 AuthProvider 实现。"""

    def __init__(self, session_factory: SessionFactory | None = None) -> None:
        # get_session_factory() 返回 async_sessionmaker，需再 () 得到 AsyncSession
        self._session_factory: SessionFactory = session_factory or get_session_factory()  # type: ignore[assignment]

    async def register(self, email: str, password: str, name: str = "") -> User:
        """注册新用户，邮箱已存在则抛 AuthConflictError。"""
        async with self._session_factory() as session:
            existing = await session.execute(
                select(UserModel).where(UserModel.email == email)
            )
            if existing.scalar_one_or_none() is not None:
                raise AuthConflictError(f"email already registered: {email}")
            user = User(email=email, name=name or email.split("@")[0])
            model = UserModel(
                id=user.id,
                email=user.email,
                name=user.name,
                password_hash=_hash_password(password),
                created_at=user.created_at.isoformat(),
            )
            session.add(model)
            await session.commit()
            logger.info("user registered: %s", email)
            return user

    async def login(self, email: str, password: str) -> User:
        """校验凭据，失败则抛 AuthCredentialError。"""
        async with self._session_factory() as session:
            result = await session.execute(
                select(UserModel).where(UserModel.email == email)
            )
            model = result.scalar_one_or_none()
            if model is None or not _verify_password(password, str(model.password_hash)):
                raise AuthCredentialError("invalid email or password")
            return self._to_domain(model)

    async def get_by_id(self, user_id: str) -> User | None:
        """按 ID 查询用户。"""
        async with self._session_factory() as session:
            result = await session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            model = result.scalar_one_or_none()
            return self._to_domain(model) if model else None

    def create_guest(self) -> User:
        """创建游客会话，不持久化；展示层按 is_guest 渲染文案。"""
        return User(email="", name="")

    @staticmethod
    def _to_domain(model: UserModel) -> User:
        """ORM 行 -> 领域 User。"""
        return User(
            id=str(model.id),
            email=str(model.email),
            name=str(model.name or ""),
            password_hash=str(model.password_hash or ""),
            created_at=datetime.fromisoformat(str(model.created_at))
            if model.created_at
            else datetime.now(),
        )
