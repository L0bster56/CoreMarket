from uuid import UUID

from fastapi import APIRouter, status

from src.backend.application.user.dtos.delete_user import DeleteUserCommand
from src.backend.application.user.dtos.get_by_id import GetByIdCommand
from src.backend.presentation.api.v1.auth.dependencies import AdminUserDep
from src.backend.presentation.api.v1.auth.schemas import UserResponse
from src.backend.presentation.api.v1.core.schemas import ExceptionSchema
from src.backend.presentation.api.v1.user.dependencies import DeleteUserDep, GetUserDep

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={
        401: {"model": ExceptionSchema},
        403: {"model": ExceptionSchema},
    },
)


@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_user(user_id: UUID, uc: GetUserDep, _: AdminUserDep) -> UserResponse:
    user = await uc.execute(GetByIdCommand(user_id=user_id))
    return UserResponse.from_entity(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID, uc: DeleteUserDep, _: AdminUserDep) -> None:
    await uc.execute(DeleteUserCommand(user_id=user_id))
