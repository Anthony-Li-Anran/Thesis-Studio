"""用户领域模型。"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class User:
    """用户实体。is_guest 由 password_hash 是否为空推断。"""

    email: str
    name: str
    id: str = field(default_factory=lambda: uuid4().hex[:12])
    password_hash: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def is_guest(self) -> bool:
        """无密码哈希即为游客。"""
        return not self.password_hash
