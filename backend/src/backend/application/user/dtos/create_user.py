from dataclasses import dataclass
from uuid import UUID

from src.backend.domain.user.entity import UserRole


@dataclass
class CreateUserCommand:
    username: str
    email: str
    password: str
    role: UserRole = UserRole.user


@dataclass
class CreateUserResult:
    user_id: UUID
