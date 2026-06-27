from typing import Annotated

from fastapi import Depends

from src.backend.application.user.use_cases.delete_user import DeleteUserUseCase
from src.backend.application.user.use_cases.get_by_id import GetByIdUseCase
from src.backend.presentation.api.v1.core.dependencies import UoWDep


def get_get_user_use_case(uow: UoWDep) -> GetByIdUseCase:
    return GetByIdUseCase(uow=uow)


GetUserDep = Annotated[GetByIdUseCase, Depends(get_get_user_use_case)]


def get_delete_user_use_case(uow: UoWDep) -> DeleteUserUseCase:
    return DeleteUserUseCase(uow=uow)


DeleteUserDep = Annotated[DeleteUserUseCase, Depends(get_delete_user_use_case)]
