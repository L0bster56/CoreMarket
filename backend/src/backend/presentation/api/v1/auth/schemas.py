from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.backend.domain.user.entity import User


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class UpdateMeRequest(BaseModel):
    username: str | None = None
    avatar_url: str | None = None


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class TokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    access_token: str
    refresh_token: str
    token_type: str


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    role: str
    avatar_url: str | None
    created_at: datetime

    @classmethod
    def from_entity(cls, user: User) -> "UserResponse":
        return cls(
            id=user.id,
            username=str(user.username),
            email=str(user.email),
            role=str(user.role),
            avatar_url=user.avatar_url,
            created_at=user.created_at,
        )
