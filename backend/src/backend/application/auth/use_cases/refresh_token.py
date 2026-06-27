from dataclasses import dataclass

from src.backend.application.auth.dtos.refresh_token import (
    RefreshTokenCommand,
    RefreshTokenResult,
)
from src.backend.application.auth.errors import InActiveUserError
from src.backend.application.auth.interfaces.security.token import TokenService
from src.backend.application.shared.interfaces.uow import UnitOfWork


@dataclass
class RefreshTokenUseCase:
    """
    UseCase: обновление access и refresh токенов.

    Ответственность:
        - Декодирование refresh token
        - Получение пользователя из базы данных
        - Проверка активности пользователя
        - Генерация новых токенов
    """

    uow: UnitOfWork
    tokens: TokenService

    async def execute(self, cmd: RefreshTokenCommand) -> RefreshTokenResult:
        """
        Обновляет токены пользователя.

        Args:
            cmd (RefreshTokenCommand): refresh token пользователя

        Returns:
            RefreshTokenResult: новые access и refresh токены

        Raises:
            InActiveUserError: если пользователь не активен
        """
        async with self.uow:
            user_id = self.tokens.decode(cmd.refresh_token, True)

            user = await self.uow.users.get_by_id(user_id)

            if not user.is_active:
                raise InActiveUserError("user is not active")

            access_token = self.tokens.encode(user.id)
            refresh_token = self.tokens.encode(user.id, True)
            token_type = self.tokens.get_token_type()

            return RefreshTokenResult(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type=token_type,
            )
