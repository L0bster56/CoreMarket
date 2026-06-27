from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.application.auth.dtos.get_me import GetMeCommand
from src.backend.application.auth.use_cases.get_me import GetMeUseCase
from src.backend.application.rating.use_cases.create_rating import CreateRatingUseCase
from src.backend.application.rating.use_cases.delete_rating import DeleteRatingUseCase
from src.backend.application.rating.use_cases.get_rating import GetRatingUseCase
from src.backend.application.rating.use_cases.update_rating import UpdateRatingUseCase
from src.backend.domain.user.entity import User
from src.backend.infrastructure.db.sqlalchemy.core.uow import SqlAlchemyUnitOfWork
from src.backend.infrastructure.db.sqlalchemy.rating.repository import SqlAlchemyRatingRepository
from src.backend.infrastructure.security.jose.token import JWTTokenService
from src.backend.presentation.api.v1.auth.dependencies import CurrentUserDep
from src.backend.presentation.api.v1.core.dependencies import UoWDep, get_db, get_uow

_optional_bearer = HTTPBearer(auto_error=False)


async def get_rating_repo(session: AsyncSession = Depends(get_db)) -> SqlAlchemyRatingRepository:
    return SqlAlchemyRatingRepository(session=session)


RatingRepoDep = Annotated[SqlAlchemyRatingRepository, Depends(get_rating_repo)]


async def get_optional_user(
    token: HTTPAuthorizationCredentials | None = Depends(_optional_bearer),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> User | None:
    if token is None:
        return None
    tokens = JWTTokenService()
    uc = GetMeUseCase(uow=uow, tokens=tokens)
    try:
        return await uc.execute(GetMeCommand(token=token.credentials))
    except Exception:
        return None


OptionalUserDep = Annotated[User | None, Depends(get_optional_user)]


def get_get_rating_use_case(uow: UoWDep) -> GetRatingUseCase:
    return GetRatingUseCase(uow=uow)


GetRatingDep = Annotated[GetRatingUseCase, Depends(get_get_rating_use_case)]


def get_create_rating_use_case(uow: UoWDep, user: CurrentUserDep) -> CreateRatingUseCase:
    return CreateRatingUseCase(uow=uow, user=user)


CreateRatingDep = Annotated[CreateRatingUseCase, Depends(get_create_rating_use_case)]


def get_update_rating_use_case(uow: UoWDep, user: CurrentUserDep) -> UpdateRatingUseCase:
    return UpdateRatingUseCase(uow=uow, user=user)


UpdateRatingDep = Annotated[UpdateRatingUseCase, Depends(get_update_rating_use_case)]


def get_delete_rating_use_case(uow: UoWDep, user: CurrentUserDep) -> DeleteRatingUseCase:
    return DeleteRatingUseCase(uow=uow, user=user)


DeleteRatingDep = Annotated[DeleteRatingUseCase, Depends(get_delete_rating_use_case)]
