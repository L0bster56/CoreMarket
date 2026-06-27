from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.backend.domain.user.entity import UserRole


@dataclass
class GetMeCommand:
    token: str


@dataclass
class GetMeResult:
    id: UUID
    username: str
    email: str
    role: UserRole
    avatar_url: str | None
    is_active: bool
    created_at: datetime
