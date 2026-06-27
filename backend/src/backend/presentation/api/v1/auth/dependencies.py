from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.backend.application.auth.dtos.get_me import GetMeCommand
from src.backend.application.auth.use_cases.get_me import GetMeUseCase
from src.backend.domain.user.entity import User, UserRole
from src.backend.infrastructure.db.sqlalchemy.core.uow import SqlAlchemyUnitOfWork
from src.backend.infrastructure.security.bcrypt.hasher import BcryptHasher
from src.backend.infrastructure.security.jose.token import JWTTokenService
from src.backend.presentation.api.v1.core.dependencies import get_uow

_schema = HTTPBearer()


async def get_hasher() -> BcryptHasher:
    return BcryptHasher()


async def get_token_service() -> JWTTokenService:
    return JWTTokenService()


async def get_current_user(
        token: HTTPAuthorizationCredentials = Depends(_schema),
        tokens: JWTTokenService = Depends(get_token_service),
        uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> User:
    uc = GetMeUseCase(uow=uow, tokens=tokens)
    return await uc.execute(cmd=GetMeCommand(token=token.credentials))


CurrentUserDep = Annotated[
    User,
    Depends(get_current_user),
]


async def require_admin(user: CurrentUserDep) -> User:
    if user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


AdminUserDep = Annotated[
    User,
    Depends(require_admin),
]
