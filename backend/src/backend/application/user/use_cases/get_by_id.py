from dataclasses import dataclass

from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.application.user.dtos.get_by_id import GetByIdCommand
from src.backend.application.user.errors import UserNotFoundError
from src.backend.domain.user.entity import User


@dataclass
class GetByIdUseCase:
    """
    UseCase: получение пользователя по идентификатору.

    Ответственность:
        - Поиск пользователя по id
        - Проверка существования пользователя
    """

    uow: UnitOfWork

    async def execute(self, cmd: GetByIdCommand) -> User:
        """
        Args:
            cmd (GetByIdCommand): идентификатор пользователя

        Returns:
            User: доменная сущность пользователя

        Raises:
            UserNotFoundError: если пользователь не найден
        """
        async with self.uow:
            user = await self.uow.users.get_by_id(cmd.user_id)

            if user is None:
                raise UserNotFoundError()

            return user
