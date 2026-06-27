from dataclasses import dataclass
from enum import StrEnum

from src.backend.domain.shared.entity import BaseEntity
from src.backend.domain.shared.mixins import TimeActionMixin
from src.backend.domain.shared.value_objects.email.value_object import Email
from src.backend.domain.user.value_objects.username.value_object import Username


class UserRole(StrEnum):
    user = "user"
    admin = "admin"


@dataclass(eq=False)
class User(BaseEntity, TimeActionMixin):
    username: Username
    email: Email
    hashed_password: str
    role: UserRole
    is_active: bool = True
    avatar_url: str | None = None

    @classmethod
    def create(
            cls,
            username: str,
            email: str,
            hashed_password: str,
            role: UserRole = UserRole.user,
    ) -> "User":
        return cls(
            username=Username(username),
            email=Email(email),
            hashed_password=hashed_password,
            role=role,
        )

    def change_username(self, username: str) -> None:
        self.username = Username(username)
        self.touch()

    def change_email(self, email: str) -> None:
        self.email = Email(email)
        self.touch()

    def change_password(self, new_password: str) -> None:
        self.hashed_password = new_password
        self.touch()

    def change_avatar_url(self, avatar_url: str | None) -> None:
        self.avatar_url = avatar_url
        self.touch()

    def endure_active(self) -> bool:
        return self.is_active

    def interact(self) -> None:
        self.touch()
