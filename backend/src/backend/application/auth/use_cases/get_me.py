from dataclasses import dataclass

from src.backend.application.auth.dtos.get_me import GetMeCommand
from src.backend.application.auth.errors import InActiveUserError
from src.backend.application.auth.interfaces.security.token import TokenService
from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.application.user.errors import UserNotFoundError
from src.backend.domain.user.entity import User


@dataclass
class GetMeUseCase:
    """
    UseCase: получение текущего пользователя по токену.

    Ответственность:
        - Декодирование JWT токена
        - Поиск пользователя в базе данных
        - Проверка активности пользователя
    """

    uow: UnitOfWork
    tokens: TokenService

    async def execute(self, cmd: GetMeCommand) -> User:
        """
        Выполняет получение текущего пользователя.

        Args:
            cmd (GetMeCommand): команда с токеном доступа

        Returns:
            User: доменная сущность пользователя

        Raises:
            UserNotFoundError: если пользователь не найден
            InActiveUserError: если пользователь неактивен
        """
        async with self.uow:
            user_id = self.tokens.decode(cmd.token)

            user = await self.uow.users.get_by_id(user_id)

            if user is None:
                raise UserNotFoundError("user not found")

            if not user.is_active:
                raise InActiveUserError("user is not active")

            return user
