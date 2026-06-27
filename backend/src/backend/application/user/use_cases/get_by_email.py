from dataclasses import dataclass

from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.application.user.dtos.get_by_email import GetByEmailCommand
from src.backend.application.user.errors import UserNotFoundError
from src.backend.domain.user.entity import User


@dataclass
class GetByEmailUseCase:
    """
    UseCase: получение пользователя по email.

    Ответственность:
        - Поиск пользователя по email
        - Проверка существования пользователя
    """

    uow: UnitOfWork

    async def execute(self, cmd: GetByEmailCommand) -> User:
        """
        Args:
            cmd (GetByEmailCommand): email пользователя

        Returns:
            User: доменная сущность пользователя

        Raises:
            UserNotFoundError: если пользователь не найден
        """
        async with self.uow:
            user = await self.uow.users.get_by_email(cmd.email)

            if user is None:
                raise UserNotFoundError()

            return user
