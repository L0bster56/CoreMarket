from dataclasses import dataclass

from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.application.user.dtos.get_by_username import GetByUsernameCommand
from src.backend.application.user.errors import UserNotFoundError
from src.backend.domain.user.entity import User


@dataclass
class GetByUsernameUseCase:
    """
    UseCase: получение пользователя по username.

    Ответственность:
        - Поиск пользователя по username
        - Проверка существования пользователя
    """

    uow: UnitOfWork

    async def execute(self, cmd: GetByUsernameCommand) -> User:
        """
        Args:
            cmd (GetByUsernameCommand): username пользователя

        Returns:
            User: доменная сущность пользователя

        Raises:
            UserNotFoundError: если пользователь не найден
        """
        async with self.uow:
            user = await self.uow.users.get_by_username(cmd.username)

            if user is None:
                raise UserNotFoundError()

            return user
