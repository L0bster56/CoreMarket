from dataclasses import dataclass

from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.application.user.dtos.delete_user import DeleteUserCommand
from src.backend.application.user.errors import UserNotFoundError


@dataclass
class DeleteUserUseCase:
    """
    UseCase: удаление пользователя (Admin).

    Ответственность:
        - Поиск пользователя по id
        - Удаление пользователя из базы данных
    """

    uow: UnitOfWork

    async def execute(self, cmd: DeleteUserCommand) -> None:
        """
        Удаляет пользователя.

        Args:
            cmd (DeleteUserCommand): идентификатор пользователя

        Raises:
            UserNotFoundError: если пользователь не найден
        """
        async with self.uow:
            user = await self.uow.users.get_by_id(cmd.user_id)

            if user is None:
                raise UserNotFoundError()

            await self.uow.users.delete(user)
            await self.uow.commit()
