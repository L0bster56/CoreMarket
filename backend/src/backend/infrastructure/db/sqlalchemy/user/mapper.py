from src.backend.domain.shared.value_objects.email.value_object import Email
from src.backend.domain.user.entity import User
from src.backend.domain.user.value_objects.username.value_object import Username
from src.backend.infrastructure.db.sqlalchemy.user.model import UserModel


def to_model(user: User) -> UserModel:
    return UserModel(
        id=user.id,
        username=str(user.username),
        email=str(user.email),
        hashed_password=user.hashed_password,
        role=user.role,
        is_active=user.is_active,
        avatar_url=user.avatar_url,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )

def to_entity(user: UserModel) -> User:
    return User(
        id=user.id,
        username=Username(user.username),
        email=Email(user.email),
        hashed_password=user.hashed_password,
        role=user.role,
        is_active=user.is_active,
        avatar_url=user.avatar_url,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )