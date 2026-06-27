from dataclasses import dataclass

from src.backend.application.auth.dtos.login_user import (
    LoginUserCommand,
    LoginUserResult,
)
from src.backend.application.auth.errors import (
    AuthUserNotFoundError,
    InvalidPasswordError,
    InActiveUserError,
)
from src.backend.application.auth.interfaces.security.hasher import Hasher
from src.backend.application.auth.interfaces.security.token import TokenService
from src.backend.application.shared.interfaces.uow import UnitOfWork


@dataclass
class LoginUserUseCase:
    """
    UseCase: аутентификация пользователя (login).

    Ответственность:
        - Поиск пользователя по username
        - Проверка пароля
        - Проверка активности пользователя
        - Генерация access и refresh токенов
    """

    uow: UnitOfWork
    tokens: TokenService
    hasher: Hasher

    async def execute(self, cmd: LoginUserCommand) -> LoginUserResult:
        """
        Выполняет вход пользователя в систему.

        Args:
            cmd (LoginUserCommand): данные для входа (username + password)

        Returns:
            LoginUserResult: access_token, refresh_token и token_type

        Raises:
            AuthUserNotFoundError: если пользователь не найден
            InvalidPasswordError: если пароль неверный
            InActiveUserError: если пользователь не активен
        """
        async with self.uow:
            user = await self.uow.users.get_by_username(cmd.username)

            if user is None:
                raise AuthUserNotFoundError("invalid password or username")

            if not self.hasher.verify(cmd.password, user.hashed_password):
                raise InvalidPasswordError("invalid password or username")

            if not user.is_active:
                raise InActiveUserError("user is not active")

            access_token = self.tokens.encode(user.id)
            refresh_token = self.tokens.encode(user.id, True)
            token_type = self.tokens.get_token_type()

            user.interact()

            await self.uow.users.update(user)
            await self.uow.commit()

            return LoginUserResult(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type=token_type,
            )
